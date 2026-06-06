// Reusable Frontend Components for Organa Kanban Columns

function escapeHTML(str) {
    if (!str) return '';
    return str.replace(/[&<>'"]/g, 
        tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
    );
}

function getDragAfterElement(container, y) {
    const draggableElements = [...container.querySelectorAll('.kanban-card-item:not(.dragging)')];
    return draggableElements.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;
        if (offset < 0 && offset > closest.offset) {
            return { offset: offset, element: child };
        } else {
            return closest;
        }
    }, { offset: Number.NEGATIVE_INFINITY }).element;
}


class ColumnCard {
    /**
     * @param {Object} column - Column data object {id, name, position}
     * @param {number} index - Index in the current list
     * @param {number} totalColumns - Total count of columns
     * @param {Function} onMoveLeft - Callback to trigger move left
     * @param {Function} onMoveRight - Callback to trigger move right
     */
    constructor(column, index, totalColumns, onMoveLeft, onMoveRight) {
        this.column = column;
        this.index = index;
        this.totalColumns = totalColumns;
        this.onMoveLeft = onMoveLeft;
        this.onMoveRight = onMoveRight;
    }

    render() {
        const name = escapeHTML(this.column.name);
        
        // Generate a unique, vibrant HSL color for the column dot indicator
        const hue = (this.column.id * 137.5) % 360;
        const dotColor = `hsl(${hue}, 80%, 65%)`;

        const card = document.createElement('div');
        card.className = 'column-card';
        card.style.animation = 'fadeIn 0.4s ease-out forwards';
        
        const isScrumMaster = (window.currentUserRole === 'SM');
        const isDeveloper = (window.currentUserRole === 'DEV');
        
        let headerActionsHtml = '';
        if (isScrumMaster) {
            headerActionsHtml = `
                ${this.index > 0 ? `<button class="btn-move-left" title="Mover izquierda" style="background: transparent; border: none; color: var(--text-muted); cursor: pointer; font-size: 14px; padding: 2px 6px; transition: color 0.2s;" onmouseover="this.style.color='var(--text-main)'" onmouseout="this.style.color='var(--text-muted)'">←</button>` : ''}
                ${this.index < this.totalColumns - 1 ? `<button class="btn-move-right" title="Mover derecha" style="background: transparent; border: none; color: var(--text-muted); cursor: pointer; font-size: 14px; padding: 2px 6px; transition: color 0.2s;" onmouseover="this.style.color='var(--text-main)'" onmouseout="this.style.color='var(--text-muted)'">→</button>` : ''}
                <button class="btn-col-edit" title="Editar columna" style="background: transparent; border: none; color: #a5b4fc; cursor: pointer; font-size: 13px; padding: 2px 4px; transition: opacity 0.2s; opacity: 0.7;" onmouseover="this.style.opacity='1'" onmouseout="this.style.opacity='0.7'">✎</button>
                <button class="btn-col-delete" title="Eliminar columna" style="background: transparent; border: none; color: #fca5a5; cursor: pointer; font-size: 13px; padding: 2px 4px; transition: opacity 0.2s; opacity: 0.7;" onmouseover="this.style.opacity='1'" onmouseout="this.style.opacity='0.7'">🗑</button>
            `;
        }

        let addCardHtml = '';
        if (isDeveloper) {
            addCardHtml = `
                <button class="btn-add-card" title="Nueva tarea" style="width: 100%; background: transparent; border: 1px dashed rgba(255, 255, 255, 0.1); border-radius: 10px; color: var(--text-muted); cursor: pointer; font-size: 13px; padding: 10px; transition: all 0.2s; display: flex; align-items: center; justify-content: center; gap: 6px; font-family: inherit; margin-top: auto;" onmouseover="this.style.borderColor='rgba(99, 102, 241, 0.3)'; this.style.color='var(--text-main)'; this.style.background='rgba(255,255,255,0.01)'" onmouseout="this.style.borderColor='rgba(255, 255, 255, 0.1)'; this.style.color='var(--text-muted)'; this.style.background='transparent'">
                    + Nueva Tarjeta
                </button>
            `;
        }

        // Setup DOM inner HTML
        card.innerHTML = `
            <div class="column-header" style="margin-bottom: 16px;">
                <span class="column-title">
                    <span style="color: ${dotColor}; margin-right: 6px;">●</span> ${name}
                </span>
                <div style="display: flex; gap: 4px; align-items: center;">
                    ${headerActionsHtml}
                    <span class="column-badge" id="column-badge-${this.column.id}" style="margin-left: 6px;">0</span>
                </div>
            </div>
            <div class="column-cards-container" id="column-cards-${this.column.id}" style="display: flex; flex-direction: column; gap: 12px; margin-bottom: 16px; min-height: 20px;"></div>
            <div class="column-placeholder" id="column-placeholder-${this.column.id}" style="display: flex; align-items: center; justify-content: center; height: 80px; border: 1px dashed rgba(255, 255, 255, 0.05); border-radius: 12px; font-size: 13px; color: var(--text-muted); margin-bottom: 16px;">
                No hay tareas
            </div>
            ${addCardHtml}
        `;

        // Attach Reordering event listeners
        const moveLeftBtn = card.querySelector('.btn-move-left');
        const moveRightBtn = card.querySelector('.btn-move-right');
        const editBtn = card.querySelector('.btn-col-edit');
        const deleteBtn = card.querySelector('.btn-col-delete');
        const addCardBtn = card.querySelector('.btn-add-card');
        const cardContainer = card.querySelector('.column-cards-container');
        const placeholder = card.querySelector('.column-placeholder');
        const badgeEl = card.querySelector('.column-badge');

        // Helper to adjust placeholder and badge locally
        const updateBadgeAndPlaceholder = () => {
            const cardCount = cardContainer.querySelectorAll('.kanban-card-item').length;
            badgeEl.innerText = cardCount;
            if (cardCount === 0) {
                placeholder.style.display = 'flex';
            } else {
                placeholder.style.display = 'none';
            }
        };

        // Drag and Drop Listeners for Column Card Containers (only if Developer)
        if (isDeveloper) {
            cardContainer.addEventListener('dragover', (e) => {
                e.preventDefault();
                const dragging = document.querySelector('.dragging');
                if (dragging) {
                    const afterElement = getDragAfterElement(cardContainer, e.clientY);
                    if (afterElement == null) {
                        cardContainer.appendChild(dragging);
                    } else {
                        cardContainer.insertBefore(dragging, afterElement);
                    }
                    updateBadgeAndPlaceholder();
                }
            });

            cardContainer.addEventListener('dragenter', (e) => {
                e.preventDefault();
                card.style.background = 'rgba(255, 255, 255, 0.02)';
                card.style.borderColor = 'rgba(99, 102, 241, 0.15)';
            });

            cardContainer.addEventListener('dragleave', () => {
                card.style.background = 'rgba(255, 255, 255, 0.01)';
                card.style.borderColor = 'rgba(255, 255, 255, 0.04)';
            });

            cardContainer.addEventListener('drop', async (e) => {
                e.preventDefault();
                card.style.background = 'rgba(255, 255, 255, 0.01)';
                card.style.borderColor = 'rgba(255, 255, 255, 0.04)';
                
                const cardId = parseInt(e.dataTransfer.getData('text/plain'));
                const sourceColId = parseInt(e.dataTransfer.getData('source-column-id'));
                const targetColId = this.column.id;
                
                if (!cardId) return;

                // Find new position
                const cardsElements = [...cardContainer.querySelectorAll('.kanban-card-item')];
                const newPosition = cardsElements.findIndex(el => parseInt(el.dataset.cardId) === cardId);

                if (newPosition !== -1) {
                    // Update badge and placeholder of the target column
                    updateBadgeAndPlaceholder();

                    // If source column is different, update its badge and placeholder too
                    if (sourceColId !== targetColId) {
                        const srcContainer = document.getElementById(`column-cards-${sourceColId}`);
                        const srcPlaceholder = document.getElementById(`column-placeholder-${sourceColId}`);
                        const srcBadge = document.getElementById(`column-badge-${sourceColId}`);
                        if (srcContainer && srcPlaceholder && srcBadge) {
                            const srcCardCount = srcContainer.querySelectorAll('.kanban-card-item').length;
                            srcBadge.innerText = srcCardCount;
                            srcPlaceholder.style.display = srcCardCount === 0 ? 'flex' : 'none';
                        }
                    }

                    // Trigger persist
                    if (typeof window.handleMoveCard === 'function') {
                        await window.handleMoveCard(cardId, sourceColId, targetColId, newPosition);
                    }
                }
            });
        }

        // Trigger cards load asynchronously
        setTimeout(() => {
            if (typeof window.fetchAndRenderCards === 'function') {
                window.fetchAndRenderCards(this.column.id, cardContainer, placeholder, badgeEl);
            }
        }, 0);

        if (moveLeftBtn) {
            moveLeftBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                if (typeof this.onMoveLeft === 'function') {
                    this.onMoveLeft(this.column.id);
                }
            });
        }

        if (moveRightBtn) {
            moveRightBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                if (typeof this.onMoveRight === 'function') {
                    this.onMoveRight(this.column.id);
                }
            });
        }

        if (editBtn) {
            editBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                if (typeof window.openEditColumnModal === 'function') {
                    window.openEditColumnModal(this.column.id, this.column.name);
                }
            });
        }

        if (deleteBtn) {
            deleteBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                if (typeof window.handleDeleteColumn === 'function') {
                    window.handleDeleteColumn(this.column.id, this.column.name);
                }
            });
        }

        if (addCardBtn) {
            addCardBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                if (typeof window.openCreateCardModal === 'function') {
                    window.openCreateCardModal(this.column.id);
                }
            });
        }

        return card;
    }
}

class ColumnGrid {
    /**
     * @param {HTMLElement|string} container - Mount target element or its ID
     * @param {Array} columns - List of column objects
     * @param {Function} onReorder - Callback to handle reordering API requests
     */
    constructor(container, columns, onReorder) {
        this.container = typeof container === 'string' ? document.getElementById(container) : container;
        this.columns = columns;
        this.onReorder = onReorder;
    }

    render() {
        if (!this.container) return;
        this.container.innerHTML = '';

        // Dynamically adjust grid layout columns based on count
        const columnsCount = this.columns.length;
        if (columnsCount > 0) {
            this.container.style.display = 'grid';
            this.container.style.gridTemplateColumns = `repeat(${columnsCount}, 1fr)`;
            this.container.style.gap = '24px';
        }

        if (!this.columns || columnsCount === 0) {
            const empty = new ColumnEmptyState(this.container);
            empty.render();
            return;
        }

        // Reordering trigger functions
        const handleMoveLeft = (colId) => {
            const index = this.columns.findIndex(c => c.id === colId);
            if (index > 0) {
                // Swap with left neighbor
                const temp = this.columns[index];
                this.columns[index] = this.columns[index - 1];
                this.columns[index - 1] = temp;
                this.triggerReorder();
            }
        };

        const handleMoveRight = (colId) => {
            const index = this.columns.findIndex(c => c.id === colId);
            if (index < columnsCount - 1) {
                // Swap with right neighbor
                const temp = this.columns[index];
                this.columns[index] = this.columns[index + 1];
                this.columns[index + 1] = temp;
                this.triggerReorder();
            }
        };

        const fragment = document.createDocumentFragment();
        this.columns.forEach((col, idx) => {
            const cardComponent = new ColumnCard(
                col, 
                idx, 
                columnsCount, 
                handleMoveLeft, 
                handleMoveRight
            );
            fragment.appendChild(cardComponent.render());
        });
        this.container.appendChild(fragment);
    }

    triggerReorder() {
        const orderList = this.columns.map(c => c.id);
        if (typeof this.onReorder === 'function') {
            this.onReorder(orderList);
        }
    }
}

class ColumnEmptyState {
    /**
     * @param {HTMLElement|string} container - Mount target
     */
    constructor(container) {
        this.container = typeof container === 'string' ? document.getElementById(container) : container;
    }

    render() {
        if (!this.container) return;
        this.container.style.display = 'block';
        this.container.innerHTML = `
            <div class="no-boards" style="animation: fadeIn 0.4s ease-out forwards; width: 100%; text-align: center; padding: 40px; border: 1px dashed rgba(255, 255, 255, 0.08); border-radius: 18px; color: var(--text-muted);">
                Este tablero no tiene columnas creadas aún. ¡Crea la primera ahora para organizar tus tareas!
            </div>
        `;
    }
}

async function fetchAndRenderCards(columnId, cardContainer, placeholder, badgeEl) {
    try {
        const response = await fetch(`/cards/columns/${columnId}/cards`);
        const data = await response.json();
        
        if (data.status === 'success') {
            const cards = data.cards || [];
            window.boardCardsMap = window.boardCardsMap || {};
            window.boardCardsMap[columnId] = cards;
            badgeEl.innerText = cards.length;
            cardContainer.innerHTML = '';
            
            if (cards.length === 0) {
                placeholder.style.display = 'flex';
            } else {
                placeholder.style.display = 'none';
                cards.forEach(card => {
                    const cardComp = new CardCard(
                        card,
                        window.boardColumns,
                        window.handleEditCard,
                        window.handleDeleteCard,
                        window.handleMoveCard
                    );
                    cardContainer.appendChild(cardComp.render());
                });
            }
        } else {
            cardContainer.innerHTML = `<div style="font-size:11px; color:#fca5a5; padding: 10px;">Error al cargar tareas.</div>`;
        }
    } catch (error) {
        cardContainer.innerHTML = `<div style="font-size:11px; color:#fca5a5; padding: 10px;">Error de conexión.</div>`;
    }
}

window.fetchAndRenderCards = fetchAndRenderCards;
window.reloadColumnCards = function(columnId) {
    const cardContainer = document.getElementById(`column-cards-${columnId}`);
    const placeholder = document.getElementById(`column-placeholder-${columnId}`);
    const badgeEl = document.getElementById(`column-badge-${columnId}`);
    if (cardContainer && placeholder && badgeEl) {
        fetchAndRenderCards(columnId, cardContainer, placeholder, badgeEl);
    }
};

// Export to global scope
window.ColumnCard = ColumnCard;
window.ColumnGrid = ColumnGrid;
window.ColumnEmptyState = ColumnEmptyState;
