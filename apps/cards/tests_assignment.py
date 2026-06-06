import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError, PermissionDenied
from django.urls import reverse
from apps.boards.services import board_service
from apps.columns.services import column_service
from apps.cards.models import KanbanCard
from apps.cards.services import card_service, assignment_service
from apps.authentication.models import AuditLog

User = get_user_model()

class KanbanCardAssignmentTests(TestCase):
    def setUp(self):
        # 1. Crear usuarios con roles Scrum
        self.sm_user = User.objects.create_user(
            username='sm@organa.com',
            email='sm@organa.com',
            password='password123',
            role='SM'
        )
        self.po_user = User.objects.create_user(
            username='po@organa.com',
            email='po@organa.com',
            password='password123',
            role='PO'
        )
        self.dev_user1 = User.objects.create_user(
            username='dev1@organa.com',
            email='dev1@organa.com',
            password='password123',
            role='DEV'
        )
        self.dev_user2 = User.objects.create_user(
            username='dev2@organa.com',
            email='dev2@organa.com',
            password='password123',
            role='DEV'
        )
        self.other_sm = User.objects.create_user(
            username='othersm@organa.com',
            email='othersm@organa.com',
            password='password123',
            role='SM'
        )

        # 2. Crear tableros (SM es dueño de board1, other_sm de board2)
        self.board1 = board_service.create_board(self.sm_user, "Tablero SM", "Desc SM")
        self.board2 = board_service.create_board(self.other_sm, "Tablero Otro SM", "Desc Otro")

        # 3. Crear columnas
        self.column1 = column_service.create_column(self.board1, "Columna SM A")
        self.column2 = column_service.create_column(self.board2, "Columna Otro B")

        # 4. Crear tarjeta en el tablero de SM
        self.card = card_service.create_card(self.sm_user, self.column1.id, "Tarea Principal", "Detalles", "MEDIUM")

    def test_assign_user_by_scrum_master_success(self):
        """
        Verifica que el Scrum Master (dueño del tablero) pueda asignar un desarrollador a una tarjeta.
        """
        # Ejecutar servicio
        card = assignment_service.assign_user(self.sm_user, self.card.id, self.dev_user1.id)
        
        self.assertEqual(card.assigned_to, self.dev_user1)
        self.assertEqual(card.assigned_by, self.sm_user)
        self.assertIsNotNone(card.assigned_at)
        
        # Verificar log de auditoría
        audit_exists = AuditLog.objects.filter(
            user=self.sm_user,
            action='CARD_ASSIGN',
            description__contains=f"asignada a {self.dev_user1.email}"
        ).exists()
        self.assertTrue(audit_exists)

    def test_reassign_user_by_scrum_master_success(self):
        """
        Verifica que el Scrum Master pueda reasignar una tarjeta de un desarrollador a otro.
        """
        # Asignar primero a dev1
        assignment_service.assign_user(self.sm_user, self.card.id, self.dev_user1.id)
        
        # Reasignar a dev2
        card = assignment_service.reassign_user(self.sm_user, self.card.id, self.dev_user2.id)
        
        self.assertEqual(card.assigned_to, self.dev_user2)
        
        # Verificar log de auditoría
        audit_exists = AuditLog.objects.filter(
            user=self.sm_user,
            action='CARD_REASSIGN',
            description__contains=f"reasignada de {self.dev_user1.email} a {self.dev_user2.email}"
        ).exists()
        self.assertTrue(audit_exists)

    def test_unassign_user_by_scrum_master_success(self):
        """
        Verifica que el Scrum Master pueda remover la asignación de una tarjeta.
        """
        # Asignar primero
        assignment_service.assign_user(self.sm_user, self.card.id, self.dev_user1.id)
        
        # Remover asignación
        card = assignment_service.unassign_user(self.sm_user, self.card.id)
        
        self.assertNil = self.assertIsNone(card.assigned_to)
        self.assertNil = self.assertIsNone(card.assigned_at)
        self.assertNil = self.assertIsNone(card.assigned_by)
        
        # Verificar log de auditoría
        audit_exists = AuditLog.objects.filter(
            user=self.sm_user,
            action='CARD_UNASSIGN',
            description__contains="desasignada"
        ).exists()
        self.assertTrue(audit_exists)

    def test_assignment_by_non_scrum_master_forbidden(self):
        """
        Verifica que roles diferentes a Scrum Master (Developer, Product Owner) no puedan asignar tareas.
        """
        # Intentar con Developer
        with self.assertRaises(PermissionDenied):
            assignment_service.assign_user(self.dev_user1, self.card.id, self.dev_user2.id)
            
        # Intentar con Product Owner
        with self.assertRaises(PermissionDenied):
            assignment_service.assign_user(self.po_user, self.card.id, self.dev_user1.id)

    def test_assignment_on_non_owned_board_forbidden(self):
        """
        Verifica que un Scrum Master no pueda asignar usuarios en tableros de los que no es propietario.
        """
        with self.assertRaises(PermissionDenied):
            # other_sm intenta asignar en el tablero de sm_user
            assignment_service.assign_user(self.other_sm, self.card.id, self.dev_user1.id)

    def test_get_user_cards_developer_only_self(self):
        """
        Verifica que un Developer sólo pueda consultar sus propias tareas asignadas.
        """
        # Asignar tarea a dev1
        assignment_service.assign_user(self.sm_user, self.card.id, self.dev_user1.id)
        
        # Consultar sus propias tareas
        dev1_cards = assignment_service.get_user_cards(self.dev_user1, self.dev_user1.id)
        self.assertIn(self.card, dev1_cards)
        
        # Intentar consultar las tareas de dev2 (debe dar PermissionDenied)
        with self.assertRaises(PermissionDenied):
            assignment_service.get_user_cards(self.dev_user1, self.dev_user2.id)

    def test_get_user_cards_po_and_sm_can_view_all(self):
        """
        Verifica que Product Owners y Scrum Masters puedan consultar las tareas asignadas a cualquier usuario.
        """
        # Asignar tarea a dev1
        assignment_service.assign_user(self.sm_user, self.card.id, self.dev_user1.id)
        
        # Scrum Master consulta dev1
        sm_query = assignment_service.get_user_cards(self.sm_user, self.dev_user1.id)
        self.assertIn(self.card, sm_query)
        
        # Product Owner consulta dev1
        po_query = assignment_service.get_user_cards(self.po_user, self.dev_user1.id)
        self.assertIn(self.card, po_query)

    def test_assign_api_views(self):
        """
        Verifica los flujos de asignación, reasignación, desasignación y consulta a nivel API (HTTP).
        """
        self.client.force_login(self.sm_user)
        
        # 1. POST /cards/{id}/assign
        url_assign = reverse('assign_card', kwargs={'card_id': self.card.id})
        response = self.client.post(
            url_assign,
            data=json.dumps({'user_id': self.dev_user1.id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        
        # 2. PUT/POST /cards/{id}/reassign
        url_reassign = reverse('reassign_card', kwargs={'card_id': self.card.id})
        response = self.client.post(
            url_reassign,
            data=json.dumps({'user_id': self.dev_user2.id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        
        # 3. GET /cards/users/{id}/cards (SM consulta dev2)
        url_workload = reverse('get_user_cards', kwargs={'user_id': self.dev_user2.id})
        response = self.client.get(url_workload)
        self.assertEqual(response.status_code, 200)
        cards = response.json()['cards']
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0]['id'], self.card.id)
        
        # 4. DELETE/POST /cards/{id}/unassign
        url_unassign = reverse('unassign_card', kwargs={'card_id': self.card.id})
        response = self.client.post(url_unassign)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        
        # Verificar desasignado
        self.card.refresh_from_db()
        self.assertIsNone(self.card.assigned_to)

    def test_api_view_developer_workload_lock(self):
        """
        Verifica que el endpoint de carga de trabajo bloquee a desarrolladores que consultan a otros.
        """
        self.client.force_login(self.dev_user1)
        
        # Consultar a sí mismo -> 200
        url_self = reverse('get_user_cards', kwargs={'user_id': self.dev_user1.id})
        response = self.client.get(url_self)
        self.assertEqual(response.status_code, 200)
        
        # Consultar a dev2 -> 403
        url_other = reverse('get_user_cards', kwargs={'user_id': self.dev_user2.id})
        response = self.client.get(url_other)
        self.assertEqual(response.status_code, 403)
