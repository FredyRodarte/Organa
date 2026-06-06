// Reusable Frontend Components for Organa Kanban Columns

function escapeHTML(str) {
    if (!str) return '';
    return str.replace(/[&<>'"]/g, 
        tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
    );
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
        
        // Setup DOM inner HTML
        card.innerHTML = `
            <div class="column-header">
                <span class="column-title">
                    <span style="color: ${dotColor}; margin-right: 6px;">●</span> ${name}
                </span>
                <div style="display: flex; gap: 4px; align-items: center;">
                    ${this.index > 0 ? `<button class="btn-move-left" title="Mover izquierda" style="background: transparent; border: none; color: var(--text-muted); cursor: pointer; font-size: 14px; padding: 2px 6px; transition: color 0.2s;" onmouseover="this.style.color='var(--text-main)'" onmouseout="this.style.color='var(--text-muted)'">←</button>` : ''}
                    ${this.index < this.totalColumns - 1 ? `<button class="btn-move-right" title="Mover derecha" style="background: transparent; border: none; color: var(--text-muted); cursor: pointer; font-size: 14px; padding: 2px 6px; transition: color 0.2s;" onmouseover="this.style.color='var(--text-main)'" onmouseout="this.style.color='var(--text-muted)'">→</button>` : ''}
                    <span class="column-badge" style="margin-left: 6px;">0</span>
                </div>
            </div>
            <div class="column-placeholder" style="flex-grow: 1; display: flex; align-items: center; justify-content: center;">
                No hay tareas
            </div>
        `;

        // Attach Reordering event listeners
        const moveLeftBtn = card.querySelector('.btn-move-left');
        const moveRightBtn = card.querySelector('.btn-move-right');

        if (moveLeftBtn) {
            moveLeftBtn.addEventListener('click', () => {
                if (typeof this.onMoveLeft === 'function') {
                    this.onMoveLeft(this.column.id);
                }
            });
        }

        if (moveRightBtn) {
            moveRightBtn.addEventListener('click', () => {
                if (typeof this.onMoveRight === 'function') {
                    this.onMoveRight(this.column.id);
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

// Export to global scope
window.ColumnCard = ColumnCard;
window.ColumnGrid = ColumnGrid;
window.ColumnEmptyState = ColumnEmptyState;
