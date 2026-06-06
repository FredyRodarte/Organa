// Reusable Frontend Components for Organa Kanban Cards

class CardCard {
    /**
     * @param {Object} card - Card data object {id, title, description, priority, column_id}
     * @param {Array} allColumns - All columns on this board to generate the move dropdown
     * @param {Function} onEdit - Callback to open edit modal
     * @param {Function} onDelete - Callback to delete card
     * @param {Function} onMove - Callback to move card
     */
    constructor(card, allColumns, onEdit, onDelete, onMove) {
        this.card = card;
        this.allColumns = allColumns || [];
        this.onEdit = onEdit;
        this.onDelete = onDelete;
        this.onMove = onMove;
    }

    render() {
        const cardEl = document.createElement('div');
        cardEl.className = 'kanban-card-item';
        cardEl.style.cssText = `
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 14px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            position: relative;
            animation: cardFadeIn 0.3s ease-out forwards;
        `;

        // Add hover effect via JS to ensure CSS isolation
        cardEl.addEventListener('mouseenter', () => {
            cardEl.style.background = 'rgba(255, 255, 255, 0.04)';
            cardEl.style.borderColor = 'rgba(99, 102, 241, 0.25)';
            cardEl.style.boxShadow = '0 8px 20px rgba(0, 0, 0, 0.25), 0 0 10px rgba(99, 102, 241, 0.1)';
            cardEl.style.transform = 'translateY(-2px)';
        });
        cardEl.addEventListener('mouseleave', () => {
            cardEl.style.background = 'rgba(255, 255, 255, 0.02)';
            cardEl.style.borderColor = 'rgba(255, 255, 255, 0.05)';
            cardEl.style.boxShadow = 'none';
            cardEl.style.transform = 'none';
        });

        // Priority badge attributes
        let badgeBg = 'rgba(255, 255, 255, 0.06)';
        let badgeColor = 'var(--text-muted)';
        let badgeBorder = '1px solid rgba(255, 255, 255, 0.1)';
        let priorityLabel = 'Baja';

        if (this.card.priority === 'HIGH') {
            badgeBg = 'rgba(239, 68, 68, 0.12)';
            badgeColor = '#fca5a5';
            badgeBorder = '1px solid rgba(239, 68, 68, 0.25)';
            priorityLabel = 'Alta';
        } else if (this.card.priority === 'MEDIUM') {
            badgeBg = 'rgba(245, 158, 11, 0.12)';
            badgeColor = '#fde047';
            badgeBorder = '1px solid rgba(245, 158, 11, 0.25)';
            priorityLabel = 'Media';
        } else {
            badgeBg = 'rgba(99, 102, 241, 0.12)';
            badgeColor = '#a5b4fc';
            badgeBorder = '1px solid rgba(99, 102, 241, 0.25)';
            priorityLabel = 'Baja';
        }

        const escapedTitle = escapeHTML(this.card.title);
        const escapedDesc = escapeHTML(this.card.description || '');

        // Generate move selector options
        const otherColumns = this.allColumns.filter(col => col.id !== this.card.column_id);
        let moveOptionsHtml = `<option value="" disabled selected>Mover a...</option>`;
        otherColumns.forEach(col => {
            moveOptionsHtml += `<option value="${col.id}">${escapeHTML(col.name)}</option>`;
        });

        cardEl.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px;">
                <span style="display: inline-block; font-size: 10px; font-weight: 600; padding: 2px 8px; border-radius: 8px; background: ${badgeBg}; color: ${badgeColor}; border: ${badgeBorder}; text-transform: uppercase;">
                    ${priorityLabel}
                </span>
                <div class="card-actions" style="display: flex; gap: 6px; align-items: center; opacity: 0.7; transition: opacity 0.2s;">
                    <button class="btn-card-edit" title="Editar tarea" style="background: transparent; border: none; color: #a5b4fc; cursor: pointer; font-size: 12px; padding: 2px; transition: color 0.2s;">✎</button>
                    <button class="btn-card-delete" title="Eliminar tarea" style="background: transparent; border: none; color: #fca5a5; cursor: pointer; font-size: 12px; padding: 2px; transition: color 0.2s;">🗑</button>
                </div>
            </div>
            <h4 style="font-size: 14px; font-weight: 600; color: var(--text-main); margin: 0; line-height: 1.4;">${escapedTitle}</h4>
            ${escapedDesc ? `<p style="font-size: 12px; color: var(--text-muted); margin: 0; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; line-height: 1.5;">${escapedDesc}</p>` : ''}
            <div style="display: flex; justify-content: flex-end; align-items: center; margin-top: 4px; border-top: 1px solid rgba(255, 255, 255, 0.03); padding-top: 8px;">
                ${otherColumns.length > 0 ? `
                    <select class="btn-card-move-select" style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 6px; color: var(--text-muted); font-size: 11px; padding: 2px 6px; outline: none; cursor: pointer; max-width: 110px; transition: all 0.2s;" onfocus="this.style.borderColor='rgba(99, 102, 241, 0.4)'" onblur="this.style.borderColor='rgba(255, 255, 255, 0.08)'">
                        ${moveOptionsHtml}
                    </select>
                ` : ''}
            </div>
        `;

        // Event Listeners
        const editBtn = cardEl.querySelector('.btn-card-edit');
        const deleteBtn = cardEl.querySelector('.btn-card-delete');
        const moveSelect = cardEl.querySelector('.btn-card-move-select');

        if (editBtn) {
            editBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                if (typeof this.onEdit === 'function') {
                    this.onEdit(this.card);
                }
            });
        }

        if (deleteBtn) {
            deleteBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                if (typeof this.onDelete === 'function') {
                    this.onDelete(this.card.id, this.card.title, this.card.column_id);
                }
            });
        }

        if (moveSelect) {
            moveSelect.addEventListener('click', (e) => {
                e.stopPropagation(); // Stop opening card edit on click
            });
            moveSelect.addEventListener('change', (e) => {
                e.stopPropagation();
                const targetColId = parseInt(e.target.value);
                if (targetColId && typeof this.onMove === 'function') {
                    this.onMove(this.card.id, targetColId);
                }
            });
        }

        // Clicking the card itself triggers edit
        cardEl.addEventListener('click', (e) => {
            if (e.target.tagName !== 'SELECT' && e.target.tagName !== 'BUTTON' && e.target.tagName !== 'OPTION') {
                if (typeof this.onEdit === 'function') {
                    this.onEdit(this.card);
                }
            }
        });

        return cardEl;
    }
}

// Export to global scope
window.CardCard = CardCard;
