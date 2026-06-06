import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from apps.authentication.models import Role, CustomUser, AuditLog
from apps.authentication.services import rbac_service
from apps.boards.models import KanbanBoard
from apps.columns.models import KanbanColumn
from apps.cards.models import KanbanCard
from apps.user_stories.models import UserStory
from apps.tasks.models import TechnicalTask

User = get_user_model()

class RBACTests(TestCase):
    def setUp(self):
        # Asegurar de que los roles existen
        self.role_po, _ = Role.objects.get_or_create(name='PRODUCT_OWNER')
        self.role_sm, _ = Role.objects.get_or_create(name='SCRUM_MASTER')
        self.role_dev, _ = Role.objects.get_or_create(name='DEVELOPER')

        # Crear usuarios con diferentes roles
        self.user_po = User.objects.create_user(
            username='po@organa.com',
            email='po@organa.com',
            password='password123',
            role='PO'
        )
        self.user_sm = User.objects.create_user(
            username='sm@organa.com',
            email='sm@organa.com',
            password='password123',
            role='SM'
        )
        self.user_dev = User.objects.create_user(
            username='dev@organa.com',
            email='dev@organa.com',
            password='password123',
            role='DEV'
        )

        # Crear tablero owned por el PO
        self.board = KanbanBoard.objects.create(
            name="Tablero de Prueba",
            owner=self.user_po
        )
        # Crear columna
        self.column = KanbanColumn.objects.create(
            name="Por hacer",
            board=self.board,
            position=0
        )
        # Crear tarjeta
        self.card = KanbanCard.objects.create(
            title="Tarjeta de Prueba",
            column=self.column,
            position=0
        )
        # Crear historia de usuario
        self.story = UserStory.objects.create(
            title="Historia de Prueba",
            board=self.board,
            business_value=10,
            priority="HIGH",
            status="ACTIVE",
            created_by=self.user_po
        )
        # Crear tarea técnica
        self.task = TechnicalTask.objects.create(
            user_story=self.story,
            title="Subtarea de Prueba",
            estimated_hours=5,
            status="TODO"
        )

    def test_role_sync_model(self):
        """Verifica que el rol legacy de CustomUser se sincroniza con role_relation y viceversa."""
        user = User.objects.create_user(
            username='new@organa.com',
            email='new@organa.com',
            password='password123',
            role='DEV'
        )
        self.assertEqual(user.role_relation, self.role_dev)
        
        # Cambiar a PO usando role CharField
        user.role = 'PO'
        user.save()
        self.assertEqual(user.role_relation, self.role_po)
        
        # Cambiar usando rbac_service
        rbac_service.assign_role(user, 'SCRUM_MASTER')
        self.assertEqual(user.role, 'SM')
        self.assertEqual(user.role_relation, self.role_sm)

    def test_permissions_matrix(self):
        """Verifica que los permisos Scrum están asignados correctamente según el rol."""
        # PRODUCT_OWNER
        self.assertTrue(rbac_service.validate_permission(self.user_po, 'approve_stories'))
        self.assertTrue(rbac_service.validate_permission(self.user_po, 'reject_stories'))
        self.assertTrue(rbac_service.validate_permission(self.user_po, 'create_stories'))
        self.assertTrue(rbac_service.validate_permission(self.user_po, 'view_metrics'))
        self.assertFalse(rbac_service.validate_permission(self.user_po, 'manage_columns'))
        self.assertFalse(rbac_service.validate_permission(self.user_po, 'move_cards'))

        # SCRUM_MASTER
        self.assertTrue(rbac_service.validate_permission(self.user_sm, 'manage_columns'))
        self.assertTrue(rbac_service.validate_permission(self.user_sm, 'manage_board'))
        self.assertFalse(rbac_service.validate_permission(self.user_sm, 'approve_stories'))

        # DEVELOPER
        self.assertTrue(rbac_service.validate_permission(self.user_dev, 'move_cards'))
        self.assertTrue(rbac_service.validate_permission(self.user_dev, 'create_tasks'))
        self.assertFalse(rbac_service.validate_permission(self.user_dev, 'approve_stories'))

    def test_ownership_validation(self):
        """Verifica que la propiedad de recursos se valida correctamente."""
        # El PO es el dueño del tablero
        rbac_service.validate_ownership(self.user_po, self.board)
        rbac_service.validate_ownership(self.user_po, self.column)
        rbac_service.validate_ownership(self.user_po, self.card)
        rbac_service.validate_ownership(self.user_po, self.story)
        rbac_service.validate_ownership(self.user_po, self.task)

        # El DEV no es el dueño, por lo que debe lanzar PermissionDenied
        with self.assertRaises(PermissionDenied):
            rbac_service.validate_ownership(self.user_dev, self.board)

    def test_metrics_masking(self):
        """Verifica que las métricas de avance técnico se ocultan a roles no autorizados (no PO)."""
        # UserStory detail con PO (debe ver métricas)
        self.client.login(email='po@organa.com', password='password123')
        response = self.client.get(reverse('detail_story', kwargs={'story_id': self.story.id}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['story']['total_tasks'], 1)
        self.assertEqual(data['story']['total_hours'], 5)
        self.client.logout()

        # UserStory detail con DEV (debe ver 0 para métricas)
        # Hacemos que dev sea el dueño del tablero para pasar la comprobación de ownership
        self.board.owner = self.user_dev
        self.board.save()
        
        self.client.login(email='dev@organa.com', password='password123')
        response = self.client.get(reverse('detail_story', kwargs={'story_id': self.story.id}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['story']['total_tasks'], 0)
        self.assertEqual(data['story']['total_hours'], 0)
        self.client.logout()

    def test_middleware_role_protection(self):
        """Verifica que el middleware bloquea endpoints según el permiso del rol."""
        # Intentar crear una historia con DEV (debería fallar con 403 porque DEV no tiene create_stories)
        self.board.owner = self.user_dev  # Ser el dueño para pasar la comprobación de ownership
        self.board.save()
        
        self.client.login(email='dev@organa.com', password='password123')
        response = self.client.post(
            reverse('create_story'),
            data=json.dumps({
                "board_id": self.board.id,
                "title": "Nueva historia por dev",
                "business_value": 5
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        # Intentar crear una historia con PO (debería tener éxito 201)
        self.board.owner = self.user_po
        self.board.save()
        self.client.login(email='po@organa.com', password='password123')
        response = self.client.post(
            reverse('create_story'),
            data=json.dumps({
                "board_id": self.board.id,
                "title": "Nueva historia por po",
                "business_value": 5
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        self.client.logout()

    def test_audit_logs_creation(self):
        """Verifica que se crean registros de auditoría al realizar acciones clave."""
        initial_logs_count = AuditLog.objects.count()
        
        # Registrar una acción usando rbac_service
        rbac_service.log_action(self.user_po, 'TEST_ACTION', 'Descripción de prueba')
        self.assertEqual(AuditLog.objects.count(), initial_logs_count + 1)
        
        last_log = AuditLog.objects.last()
        self.assertEqual(last_log.user, self.user_po)
        self.assertEqual(last_log.action, 'TEST_ACTION')
        self.assertEqual(last_log.description, 'Descripción de prueba')
