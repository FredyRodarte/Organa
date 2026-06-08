import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError, PermissionDenied
from django.urls import reverse
from apps.boards.services import board_service
from apps.columns.services import column_service
from apps.cards.models import KanbanCard
from apps.cards.services import card_service, assignment_service
from apps.user_stories.models import UserStory
from apps.metrics.services import metrics_service

User = get_user_model()

class KanbanMetricsTests(TestCase):
    def setUp(self):
        # 1. Crear usuarios con roles Scrum
        self.po_user = User.objects.create_user(
            username='po_metrics@organa.com',
            email='po_metrics@organa.com',
            password='password123',
            role='PO'
        )
        self.sm_user = User.objects.create_user(
            username='sm_metrics@organa.com',
            email='sm_metrics@organa.com',
            password='password123',
            role='SM'
        )
        self.dev_user = User.objects.create_user(
            username='dev_metrics@organa.com',
            email='dev_metrics@organa.com',
            password='password123',
            role='DEV'
        )
        self.other_dev = User.objects.create_user(
            username='otherdev_metrics@organa.com',
            email='otherdev_metrics@organa.com',
            password='password123',
            role='DEV'
        )

        # 2. Crear tableros
        self.board = board_service.create_board(self.po_user, "Tablero de Metricas", "Descripcion")

        # 3. Crear columnas ("Todo", "In Progress", "Done")
        self.col_todo = column_service.create_column(self.board, "Por Hacer")
        self.col_in_progress = column_service.create_column(self.board, "En Progreso")
        self.col_done = column_service.create_column(self.board, "Hecho")

        # 4. Crear historias de usuario
        self.story1 = UserStory.objects.create(
            board=self.board,
            created_by=self.po_user,
            title="Historia Aprobada",
            approval_status='APPROVED'
        )
        self.story2 = UserStory.objects.create(
            board=self.board,
            created_by=self.po_user,
            title="Historia Pendiente",
            approval_status='PENDING'
        )
        self.story3 = UserStory.objects.create(
            board=self.board,
            created_by=self.po_user,
            title="Historia Cambios",
            approval_status='CHANGES_REQUESTED'
        )

        # 5. Crear tarjetas y asociar a historias y asignados
        self.card1 = card_service.create_card(self.po_user, self.col_todo.id, "Tarea 1")
        self.card1.user_story = self.story1
        self.card1.save()
        
        self.card2 = card_service.create_card(self.po_user, self.col_in_progress.id, "Tarea 2")
        self.card2.user_story = self.story2
        self.card2.assigned_to = self.dev_user
        self.card2.save()
        
        self.card3 = card_service.create_card(self.po_user, self.col_done.id, "Tarea 3")
        self.card3.user_story = self.story1
        self.card3.assigned_to = self.dev_user
        self.card3.save()
        
        self.card4 = card_service.create_card(self.po_user, self.col_done.id, "Tarea 4")
        self.card4.assigned_to = self.other_dev
        self.card4.save()

    def test_get_completion_rate(self):
        """
        Verifica el cálculo de porcentaje de completitud.
        """
        self.assertEqual(metrics_service.get_completion_rate(1, 4), 25.0)
        self.assertEqual(metrics_service.get_completion_rate(0, 0), 0.0)
        self.assertEqual(metrics_service.get_completion_rate(2, 3), 66.7)

    def test_get_board_metrics_po_sm(self):
        """
        Product Owner y Scrum Master deben ver todas las métricas del tablero.
        """
        # Test PO
        metrics = metrics_service.get_board_metrics(self.po_user, self.board.id)
        self.assertEqual(metrics['total_cards'], 4)
        self.assertEqual(metrics['completed_cards'], 2)  # card3 y card4 están en la columna "Hecho"
        self.assertEqual(metrics['pending_cards'], 2)    # card1 en "Por Hacer", card2 en "En Progreso"
        self.assertEqual(metrics['completion_rate'], 50.0)
        
        # Test SM
        metrics_sm = metrics_service.get_board_metrics(self.sm_user, self.board.id)
        self.assertEqual(metrics_sm['total_cards'], 4)

    def test_get_board_metrics_developer_filtered(self):
        """
        El Developer sólo debe ver métricas de tarjetas asignadas a él.
        """
        metrics = metrics_service.get_board_metrics(self.dev_user, self.board.id)
        # dev_user tiene asignadas card2 y card3
        self.assertEqual(metrics['total_cards'], 2)
        self.assertEqual(metrics['completed_cards'], 1)  # card3 está en "Hecho"
        self.assertEqual(metrics['pending_cards'], 1)    # card2 está en "En Progreso"
        self.assertEqual(metrics['completion_rate'], 50.0)

    def test_get_story_metrics_po_sm(self):
        """
        PO y SM deben ver todas las historias del tablero agrupadas por estado.
        """
        metrics = metrics_service.get_story_metrics(self.po_user, self.board.id)
        self.assertEqual(metrics['total_stories'], 3)
        self.assertEqual(metrics['approved_stories'], 1)
        self.assertEqual(metrics['pending_stories'], 1)
        self.assertEqual(metrics['changes_requested_stories'], 1)

    def test_get_story_metrics_developer_filtered(self):
        """
        El Developer sólo debe ver métricas de historias con tarjetas asignadas a él.
        """
        metrics = metrics_service.get_story_metrics(self.dev_user, self.board.id)
        # dev_user tiene card2 (asociada a story2 - PENDING) y card3 (asociada a story1 - APPROVED)
        # No tiene tarjetas asociadas a story3 (CHANGES_REQUESTED)
        self.assertEqual(metrics['total_stories'], 2)
        self.assertEqual(metrics['approved_stories'], 1)
        self.assertEqual(metrics['pending_stories'], 1)
        self.assertEqual(metrics['changes_requested_stories'], 0)

    def test_get_assignment_metrics_po_sm(self):
        """
        PO y SM pueden ver la carga de trabajo de todos los desarrolladores.
        """
        workload = metrics_service.get_assignment_metrics(self.sm_user, self.board.id)
        # dev_user tiene 2 tarjetas, other_dev tiene 1
        self.assertEqual(len(workload), 2)
        self.assertEqual(workload[0]['email'], self.dev_user.email)
        self.assertEqual(workload[0]['count'], 2)
        self.assertEqual(workload[1]['email'], self.other_dev.email)
        self.assertEqual(workload[1]['count'], 1)

    def test_get_assignment_metrics_developer_locked(self):
        """
        El Developer tiene prohibido ver la carga de trabajo del equipo.
        """
        with self.assertRaises(PermissionDenied):
            metrics_service.get_assignment_metrics(self.dev_user, self.board.id)

    def test_metrics_api_views(self):
        """
        Verifica el comportamiento de los endpoints HTTP correspondientes.
        """
        # 1. Login como PO
        self.client.force_login(self.po_user)
        
        # Test Board API
        response = self.client.get(reverse('board_metrics', kwargs={'board_id': self.board.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['metrics']['total_cards'], 4)
        
        # Test Stories API
        response = self.client.get(reverse('story_metrics', kwargs={'board_id': self.board.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['metrics']['total_stories'], 3)
        
        # Test Team API
        response = self.client.get(reverse('team_metrics', kwargs={'board_id': self.board.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['workload']), 2)

        # 2. Login como Developer
        self.client.force_login(self.dev_user)
        
        # Test Board API (personal)
        response = self.client.get(reverse('board_metrics', kwargs={'board_id': self.board.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['metrics']['total_cards'], 2)
        
        # Test Team API (bloqueado para desarrollador -> 403)
        response = self.client.get(reverse('team_metrics', kwargs={'board_id': self.board.id}))
        self.assertEqual(response.status_code, 403)
