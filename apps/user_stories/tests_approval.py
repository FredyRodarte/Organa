import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError, PermissionDenied
from django.urls import reverse
from django.utils import timezone
from apps.boards.services import board_service
from apps.user_stories.services import user_story_service, approval_service
from apps.user_stories.models import UserStory

User = get_user_model()

class UserStoryApprovalServiceTests(TestCase):
    def setUp(self):
        # Crear usuarios de prueba
        self.po_user = User.objects.create_user(
            username='po@organa.com',
            email='po@organa.com',
            password='password123',
            role='PO'
        )
        self.dev_user = User.objects.create_user(
            username='dev@organa.com',
            email='dev@organa.com',
            password='password123',
            role='DEV'
        )
        self.other_po = User.objects.create_user(
            username='other_po@organa.com',
            email='other_po@organa.com',
            password='password123',
            role='PO'
        )

        # Crear tablero de prueba
        self.board = board_service.create_board(self.po_user, "Tablero de Prueba PO")
        
        # Crear historia de prueba
        # Nota: La historia se crea en el tablero de po_user
        self.story = user_story_service.create_story(self.po_user, self.board.id, "Historia para Validar")

    def test_approve_story_success(self):
        """
        Verifica que un Product Owner apruebe correctamente una historia de usuario.
        """
        story = approval_service.approve_story(self.po_user, self.story.id)
        self.assertEqual(story.approval_status, 'APPROVED')
        self.assertEqual(story.approved_by, self.po_user)
        self.assertIsNotNone(story.approved_at)
        self.assertIsNone(story.rejection_reason)

    def test_approve_story_developer_denied(self):
        """
        Verifica que un Developer reciba PermissionDenied al intentar aprobar.
        """
        with self.assertRaises(PermissionDenied):
            approval_service.approve_story(self.dev_user, self.story.id)

    def test_approve_story_non_board_owner_po_denied(self):
        """
        Verifica que un Product Owner que no es dueño del tablero reciba PermissionDenied.
        """
        with self.assertRaises(PermissionDenied):
            approval_service.approve_story(self.other_po, self.story.id)

    def test_reject_story_success(self):
        """
        Verifica que un Product Owner rechace correctamente una historia especificando un motivo.
        """
        story = approval_service.reject_story(self.po_user, self.story.id, "Faltan especificaciones técnicas.")
        self.assertEqual(story.approval_status, 'REJECTED')
        self.assertEqual(story.rejection_reason, "Faltan especificaciones técnicas.")
        self.assertEqual(story.approved_by, self.po_user)
        self.assertIsNotNone(story.approved_at)

    def test_reject_story_missing_reason(self):
        """
        Verifica que rechazar sin especificar un motivo lance ValidationError.
        """
        with self.assertRaises(ValidationError) as ctx:
            approval_service.reject_story(self.po_user, self.story.id, "   ")
        self.assertIn("El motivo de rechazo es obligatorio", str(ctx.exception))

    def test_request_changes_success(self):
        """
        Verifica que un Product Owner solicite ajustes especificando los cambios.
        """
        story = approval_service.request_changes(self.po_user, self.story.id, "Ajustar estimaciones de horas.")
        self.assertEqual(story.approval_status, 'CHANGES_REQUESTED')
        self.assertEqual(story.rejection_reason, "Ajustar estimaciones de horas.")
        self.assertEqual(story.approved_by, self.po_user)
        self.assertIsNotNone(story.approved_at)

    def test_request_changes_missing_reason(self):
        """
        Verifica que solicitar cambios sin motivo lance ValidationError.
        """
        with self.assertRaises(ValidationError) as ctx:
            approval_service.request_changes(self.po_user, self.story.id, "")
        self.assertIn("Debes especificar los cambios solicitados", str(ctx.exception))


class UserStoryApprovalAPITests(TestCase):
    def setUp(self):
        self.po_user = User.objects.create_user(
            username='po2@organa.com',
            email='po2@organa.com',
            password='password123',
            role='PO'
        )
        self.dev_user = User.objects.create_user(
            username='dev2@organa.com',
            email='dev2@organa.com',
            password='password123',
            role='DEV'
        )
        self.board = board_service.create_board(self.po_user, "Tablero API PO")
        self.story = user_story_service.create_story(self.po_user, self.board.id, "Story API")

    def test_approve_story_view_success(self):
        """
        Verifica el endpoint de aprobación con un usuario PO autenticado.
        """
        self.client.login(email='po2@organa.com', password='password123')
        response = self.client.post(
            reverse('approve_story', kwargs={'story_id': self.story.id})
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['story']['approval_status'], 'APPROVED')
        self.assertEqual(data['story']['approved_by_email'], self.po_user.email)

    def test_approve_story_view_permission_denied(self):
        """
        Verifica que el endpoint de aprobación devuelva 403 Forbidden para un DEV.
        """
        self.client.login(email='dev2@organa.com', password='password123')
        response = self.client.post(
            reverse('approve_story', kwargs={'story_id': self.story.id})
        )
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertEqual(data['status'], 'error')

    def test_reject_story_view_success(self):
        """
        Verifica el endpoint de rechazo con un PO y motivo en el cuerpo de la petición.
        """
        self.client.login(email='po2@organa.com', password='password123')
        response = self.client.post(
            reverse('reject_story', kwargs={'story_id': self.story.id}),
            data=json.dumps({"reason": "Motivo de rechazo por API"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['story']['approval_status'], 'REJECTED')
        self.assertEqual(data['story']['rejection_reason'], 'Motivo de rechazo por API')

    def test_request_changes_view_success(self):
        """
        Verifica el endpoint de solicitar cambios con un PO y motivo en el cuerpo.
        """
        self.client.login(email='po2@organa.com', password='password123')
        response = self.client.post(
            reverse('request_changes', kwargs={'story_id': self.story.id}),
            data=json.dumps({"reason": "Cambiar la descripción de aceptación"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['story']['approval_status'], 'CHANGES_REQUESTED')
        self.assertEqual(data['story']['rejection_reason'], 'Cambiar la descripción de aceptación')

    def test_toggle_role_view_success(self):
        """
        Verifica el endpoint para alternar el rol simulado del usuario actual.
        """
        self.client.login(email='dev2@organa.com', password='password123')
        response = self.client.post(reverse('toggle_role'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['role'], 'PO')
        
        # Verificar cambio en BD
        self.dev_user.refresh_from_db()
        self.assertEqual(self.dev_user.role, 'PO')
