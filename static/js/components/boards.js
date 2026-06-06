// Reusable Frontend Components for Organa Kanban Boards

// Helper to escape HTML to prevent XSS injection
function escapeHTML(str) {
    if (!str) return '';
    return str.replace(/[&<>'"]/g, 
        tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
    );
}

class BoardCard {
    /**
     * @param {Object} board - Board data object {id, name, description, created_at}
     */
    constructor(board) {
        this.board = board;
    }

    render() {
        const boardUrl = `/boards/${this.board.id}/`;
        const name = escapeHTML(this.board.name);
        const description = escapeHTML(this.board.description) || '<em style="opacity: 0.5;">Sin descripción</em>';
        const date = this.board.created_at ? this.board.created_at.split(' ')[0] : '';

        const card = document.createElement('div');
        card.className = 'board-card';
        card.style.animation = 'fadeIn 0.4s ease-out forwards';
        card.style.cursor = 'pointer';
        
        // Navigation handler
        card.addEventListener('click', () => {
            window.location.href = boardUrl;
        });

        // Setup DOM inner HTML (including structured actions container)
        card.innerHTML = `
            <div>
                <h3 class="board-name">${name}</h3>
                <p class="board-desc">${description}</p>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: auto; border-top: 1px solid rgba(255, 255, 255, 0.04); padding-top: 12px;">
                <span class="board-date">Creado: ${date}</span>
                <div style="display: flex; gap: 8px; position: relative; z-index: 10;">
                    <button class="btn-card-edit" style="background: transparent; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 6px; padding: 4px 8px; font-size: 11px; font-weight: 600; color: #a5b4fc; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.borderColor='rgba(99, 102, 241, 0.5)'" onmouseout="this.style.borderColor='rgba(255, 255, 255, 0.1)'">Editar</button>
                    <button class="btn-card-delete" style="background: transparent; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 6px; padding: 4px 8px; font-size: 11px; font-weight: 600; color: #fca5a5; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.borderColor='rgba(239, 68, 68, 0.5)'" onmouseout="this.style.borderColor='rgba(255, 255, 255, 0.1)'">Eliminar</button>
                </div>
            </div>
        `;

        // Intercept action button clicks using stopPropagation
        const editBtn = card.querySelector('.btn-card-edit');
        const deleteBtn = card.querySelector('.btn-card-delete');

        editBtn.addEventListener('click', (event) => {
            event.stopPropagation();
            if (typeof window.openEditModal === 'function') {
                window.openEditModal(this.board.id, this.board.name, this.board.description || '');
            }
        });

        deleteBtn.addEventListener('click', (event) => {
            event.stopPropagation();
            if (typeof window.handleDeleteBoard === 'function') {
                window.handleDeleteBoard(this.board.id, this.board.name);
            }
        });

        return card;
    }
}

class BoardGrid {
    /**
     * @param {HTMLElement|string} container - Mount target element or its ID
     * @param {Array} boards - List of board objects
     */
    constructor(container, boards) {
        this.container = typeof container === 'string' ? document.getElementById(container) : container;
        this.boards = boards;
    }

    render() {
        if (!this.container) return;
        this.container.innerHTML = '';
        
        if (!this.boards || this.boards.length === 0) {
            const empty = new EmptyState(this.container);
            empty.render();
            return;
        }

        const fragment = document.createDocumentFragment();
        this.boards.forEach(board => {
            const cardComponent = new BoardCard(board);
            fragment.appendChild(cardComponent.render());
        });
        this.container.appendChild(fragment);
    }
}

class EmptyState {
    /**
     * @param {HTMLElement|string} container - Mount target element or its ID
     * @param {string} message - Spanish empty state message
     */
    constructor(container, message = "No tienes tableros creados aún. ¡Crea el primero ahora!") {
        this.container = typeof container === 'string' ? document.getElementById(container) : container;
        this.message = message;
    }

    render() {
        if (!this.container) return;
        this.container.innerHTML = `
            <div class="no-boards" style="animation: fadeIn 0.4s ease-out forwards; width: 100%;">
                ${escapeHTML(this.message)}
            </div>
        `;
    }
}

// Export to global scope for Django templates usage
window.BoardCard = BoardCard;
window.BoardGrid = BoardGrid;
window.EmptyState = EmptyState;
