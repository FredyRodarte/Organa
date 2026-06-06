// Reusable Frontend Components for Organa User Stories

if (typeof escapeHTML === 'undefined') {
    window.escapeHTML = function(str) {
        if (!str) return '';
        return str.replace(/[&<>'"]/g, 
            tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
        );
    };
}

class StoryCard {
    /**
     * @param {Object} story - Story data
     * @param {Function} onViewDetail - Callback to open detail view
     */
    constructor(story, onViewDetail) {
        this.story = story;
        this.onViewDetail = onViewDetail;
    }

    render() {
        const cardEl = document.createElement('div');
        cardEl.className = 'story-card-item';
        cardEl.style.cssText = `
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            animation: cardFadeIn 0.3s ease-out forwards;
        `;

        cardEl.addEventListener('mouseenter', () => {
            cardEl.style.background = 'rgba(255, 255, 255, 0.04)';
            cardEl.style.borderColor = 'rgba(139, 92, 246, 0.3)';
            cardEl.style.boxShadow = '0 6px 16px rgba(0, 0, 0, 0.2), 0 0 8px rgba(139, 92, 246, 0.1)';
            cardEl.style.transform = 'translateY(-1px)';
        });
        cardEl.addEventListener('mouseleave', () => {
            cardEl.style.background = 'rgba(255, 255, 255, 0.02)';
            cardEl.style.borderColor = 'rgba(255, 255, 255, 0.05)';
            cardEl.style.boxShadow = 'none';
            cardEl.style.transform = 'none';
        });

        // Priority badges
        let priBg = 'rgba(255, 255, 255, 0.06)';
        let priColor = 'var(--text-muted)';
        let priBorder = '1px solid rgba(255, 255, 255, 0.1)';
        let priLabel = 'Baja';

        if (this.story.priority === 'HIGH') {
            priBg = 'rgba(239, 68, 68, 0.12)';
            priColor = '#fca5a5';
            priBorder = '1px solid rgba(239, 68, 68, 0.25)';
            priLabel = 'Alta';
        } else if (this.story.priority === 'MEDIUM') {
            priBg = 'rgba(245, 158, 11, 0.12)';
            priColor = '#fde047';
            priBorder = '1px solid rgba(245, 158, 11, 0.25)';
            priLabel = 'Media';
        } else {
            priBg = 'rgba(99, 102, 241, 0.12)';
            priColor = '#a5b4fc';
            priBorder = '1px solid rgba(99, 102, 241, 0.25)';
            priLabel = 'Baja';
        }

        // Status badges
        let statBg = 'rgba(59, 130, 246, 0.12)';
        let statColor = '#93c5fd';
        let statLabel = 'Activa';

        if (this.story.status === 'COMPLETED') {
            statBg = 'rgba(16, 185, 129, 0.12)';
            statColor = '#a7f3d0';
            statLabel = 'Completada';
        } else if (this.story.status === 'ARCHIVED') {
            statBg = 'rgba(156, 163, 175, 0.12)';
            statColor = '#d1d5db';
            statLabel = 'Archivada';
        }

        // Approval status badges
        let appBg = 'rgba(245, 158, 11, 0.12)';
        let appColor = '#fbbf24';
        let appBorder = '1px solid rgba(245, 158, 11, 0.25)';
        let appLabel = 'Pendiente';

        const appStatus = this.story.approval_status || 'PENDING';
        if (appStatus === 'APPROVED') {
            appBg = 'rgba(16, 185, 129, 0.12)';
            appColor = '#34d399';
            appBorder = '1px solid rgba(16, 185, 129, 0.25)';
            appLabel = 'Aprobada';
        } else if (appStatus === 'REJECTED') {
            appBg = 'rgba(239, 68, 68, 0.12)';
            appColor = '#fca5a5';
            appBorder = '1px solid rgba(239, 68, 68, 0.25)';
            appLabel = 'Rechazada';
        } else if (appStatus === 'CHANGES_REQUESTED') {
            appBg = 'rgba(249, 115, 22, 0.12)';
            appColor = '#fdba74';
            appBorder = '1px solid rgba(249, 115, 22, 0.25)';
            appLabel = 'Ajustes';
        }

        const value = this.story.business_value || 0;
        const title = escapeHTML(this.story.title);
        const desc = escapeHTML(this.story.description || '');

        const totalTasks = this.story.total_tasks || 0;
        const completedTasks = this.story.completed_tasks || 0;
        const totalHours = this.story.total_hours || 0;
        const progressPercent = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

        const hoursBadgeHtml = `
            <span style="font-size: 10px; font-weight: 600; padding: 2px 8px; border-radius: 8px; background: rgba(59, 130, 246, 0.12); color: #93c5fd; border: 1px solid rgba(59, 130, 246, 0.25);">
                ⏱ ${totalHours}h
            </span>
        `;

        cardEl.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; gap: 6px;">
                <div style="display: flex; gap: 4px;">
                    <span style="font-size: 10px; font-weight: 600; padding: 2px 8px; border-radius: 8px; background: ${priBg}; color: ${priColor}; border: ${priBorder}; text-transform: uppercase;">
                        ${priLabel}
                    </span>
                    <span style="font-size: 10px; font-weight: 600; padding: 2px 8px; border-radius: 8px; background: ${appBg}; color: ${appColor}; border: ${appBorder}; text-transform: uppercase;">
                        ${appLabel}
                    </span>
                </div>
                <div style="display: flex; gap: 6px; align-items: center;">
                    <span style="font-size: 10px; font-weight: 600; padding: 2px 8px; border-radius: 8px; background: ${statBg}; color: ${statColor}; border: 1px solid ${statColor}30;">
                        ${statLabel}
                    </span>
                    <span style="font-size: 10px; font-weight: 600; padding: 2px 8px; border-radius: 8px; background: rgba(139, 92, 246, 0.12); color: #d8b4fe; border: 1px solid rgba(139, 92, 246, 0.25);">
                        Valor: ${value}
                    </span>
                    ${hoursBadgeHtml}
                </div>
            </div>
            <h4 style="font-size: 14px; font-weight: 600; color: var(--text-main); margin: 0; line-height: 1.4;">${title}</h4>
            ${desc ? `<p style="font-size: 12px; color: var(--text-muted); margin: 0; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; line-height: 1.5;">${desc}</p>` : ''}
            
            <!-- Progress Bar -->
            ${totalTasks > 0 ? `
            <div style="display: flex; flex-direction: column; gap: 6px; margin-top: 4px; background: rgba(255, 255, 255, 0.01); border-radius: 6px; padding: 4px 0;">
                <div style="display: flex; justify-content: space-between; font-size: 10px; color: var(--text-muted);">
                    <span>Subtareas: ${completedTasks}/${totalTasks}</span>
                    <span style="font-weight: 600; color: var(--text-main);">${progressPercent}%</span>
                </div>
                <div style="height: 6px; background: rgba(255, 255, 255, 0.05); border-radius: 3px; overflow: hidden;">
                    <div style="height: 100%; width: ${progressPercent}%; background: linear-gradient(90deg, #8b5cf6, #ec4899); border-radius: 3px; transition: width 0.3s ease;"></div>
                </div>
            </div>
            ` : ''}

            <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid rgba(255, 255, 255, 0.03); padding-top: 8px; margin-top: 4px; font-size: 11px; color: var(--text-muted);">
                <span id="story-linked-count-${this.story.id}">🔗 Cargando tareas vinculadas...</span>
                <span style="color: var(--accent); font-weight: 500;">Ver detalles →</span>
            </div>
        `;

        cardEl.addEventListener('click', () => {
            if (typeof this.onViewDetail === 'function') {
                this.onViewDetail(this.story.id);
            }
        });

        // Fetch linked cards count asynchronously
        setTimeout(async () => {
            try {
                const response = await fetch(`/stories/${this.story.id}`);
                const data = await response.json();
                const textEl = cardEl.querySelector(`#story-linked-count-${this.story.id}`);
                if (data.status === 'success' && textEl) {
                    const count = data.story.cards ? data.story.cards.length : 0;
                    textEl.innerText = count === 1 ? `🔗 1 Tarea vinculada` : `🔗 ${count} Tareas vinculadas`;
                }
            } catch (e) {
                // Ignore silent count errors
            }
        }, 0);

        return cardEl;
    }
}

class StoryDetail {
    /**
     * @param {Object} story - Full story detail data with cards list
     * @param {string} userRole - Current active role of the user ('DEV' or 'PO')
     * @param {Function} onBack - Callback to return to list view
     * @param {Function} onUpdate - Callback to update story attributes
     * @param {Function} onLinkCard - Callback to link a card
     * @param {Function} onUnlinkCard - Callback to unlink a card
     * @param {Function} onCreateTask - Callback to create a subtask
     * @param {Function} onUpdateTask - Callback to update a subtask
     * @param {Function} onDeleteTask - Callback to delete a subtask
     * @param {Function} onApprove - Callback to approve user story
     * @param {Function} onReject - Callback to reject user story
     * @param {Function} onRequestChanges - Callback to request changes on user story
     */
    constructor(story, userRole, onBack, onUpdate, onLinkCard, onUnlinkCard, onCreateTask, onUpdateTask, onDeleteTask, onApprove, onReject, onRequestChanges) {
        this.story = story;
        this.userRole = userRole || 'DEV';
        this.onBack = onBack;
        this.onUpdate = onUpdate;
        this.onLinkCard = onLinkCard;
        this.onUnlinkCard = onUnlinkCard;
        this.onCreateTask = onCreateTask;
        this.onUpdateTask = onUpdateTask;
        this.onDeleteTask = onDeleteTask;
        this.onApprove = onApprove;
        this.onReject = onReject;
        this.onRequestChanges = onRequestChanges;
    }

    render() {
        const detailEl = document.createElement('div');
        detailEl.className = 'story-detail-view';
        detailEl.style.cssText = `
            display: flex;
            flex-direction: column;
            gap: 20px;
            animation: fadeIn 0.3s ease-out forwards;
        `;

        // Filter all board cards that are NOT linked to this story
        const allCards = Object.values(window.boardCardsMap || {}).flat();
        
        // Remove duplicate cards (if any)
        const uniqueCardsMap = {};
        allCards.forEach(c => uniqueCardsMap[c.id] = c);
        const uniqueBoardCards = Object.values(uniqueCardsMap);

        const linkedCardIds = new Set(this.story.cards.map(c => c.id));
        const linkableCards = uniqueBoardCards.filter(c => !linkedCardIds.has(c.id));

        let linkableOptions = `<option value="" disabled selected>Selecciona una tarea...</option>`;
        linkableCards.forEach(c => {
            linkableOptions += `<option value="${c.id}">${escapeHTML(c.title)}</option>`;
        });

        let linkedCardsHtml = '';
        if (this.story.cards.length === 0) {
            linkedCardsHtml = `
                <div style="text-align: center; padding: 20px; border: 1px dashed rgba(255,255,255,0.05); border-radius: 8px; color: var(--text-muted); font-size: 12px;">
                    No hay tareas Kanban vinculadas a esta historia de usuario.
                </div>
            `;
        } else {
            this.story.cards.forEach(card => {
                linkedCardsHtml += `
                    <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04); border-radius: 8px; padding: 10px 12px; font-size: 13px;">
                        <span style="font-weight: 500; color: var(--text-main);">${escapeHTML(card.title)} <span style="font-size: 10px; color: var(--text-muted); margin-left: 6px;">(${escapeHTML(card.column_name)})</span></span>
                        <button class="btn-unlink-card" data-card-id="${card.id}" title="Desvincular" style="background: transparent; border: none; color: #fca5a5; cursor: pointer; font-size: 12px; padding: 2px 6px; transition: opacity 0.2s;" onmouseover="this.style.opacity='1'" onmouseout="this.style.opacity='0.7'">🗑</button>
                    </div>
                `;
            });
        }

        const totalTasks = this.story.total_tasks || 0;
        const completedTasks = this.story.completed_tasks || 0;
        const totalHours = this.story.total_hours || 0;
        const progressPercent = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

        let tasksListHtml = '';
        if (!this.story.tasks || this.story.tasks.length === 0) {
            tasksListHtml = `
                <div style="text-align: center; padding: 20px; border: 1px dashed rgba(255,255,255,0.05); border-radius: 8px; color: var(--text-muted); font-size: 12px;">
                    No hay subtareas técnicas definidas.
                </div>
            `;
        } else {
            this.story.tasks.forEach(task => {
                const isDone = task.status === 'DONE';
                const titleStyle = isDone ? 'text-decoration: line-through; color: var(--text-muted); font-style: italic;' : 'color: var(--text-main); font-weight: 500;';
                
                tasksListHtml += `
                    <div class="task-item-row" data-task-id="${task.id}" style="display: flex; align-items: center; justify-content: space-between; gap: 10px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04); border-radius: 8px; padding: 8px 12px; font-size: 13px; transition: background 0.2s;">
                        <div style="display: flex; flex-direction: column; gap: 2px; flex-grow: 1; min-width: 0;">
                            <span class="task-title" style="${titleStyle} overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${escapeHTML(task.title)}">
                                ${escapeHTML(task.title)}
                            </span>
                            <span style="font-size: 10px; color: var(--text-muted);">Estimación: ⏱ ${task.estimated_hours}h</span>
                        </div>
                        
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <!-- Status Dropdown -->
                            <select class="select-task-status form-control" data-task-id="${task.id}" style="padding: 4px 8px; font-size: 11px; width: auto; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); height: 28px;">
                                <option value="TODO" ${task.status === 'TODO' ? 'selected' : ''}>Por hacer</option>
                                <option value="IN_PROGRESS" ${task.status === 'IN_PROGRESS' ? 'selected' : ''}>En progreso</option>
                                <option value="DONE" ${task.status === 'DONE' ? 'selected' : ''}>Completado</option>
                            </select>
                            
                            <!-- Delete Button -->
                            <button class="btn-delete-task" data-task-id="${task.id}" title="Eliminar subtarea" style="background: transparent; border: none; color: #fca5a5; cursor: pointer; font-size: 12px; padding: 4px 6px; transition: opacity 0.2s; opacity: 0.7;" onmouseover="this.style.opacity='1'" onmouseout="this.style.opacity='0.7'">
                                🗑
                            </button>
                        </div>
                    </div>
                `;
            });
        }

        // Approval flow HTML block
        const appStatus = this.story.approval_status || 'PENDING';
        let statusText = 'Pendiente de aprobación';
        let statusColor = '#fbbf24';
        let statusIcon = '⏳';
        let logText = '';

        if (appStatus === 'APPROVED') {
            statusText = 'Aprobada';
            statusColor = '#34d399';
            statusIcon = '✅';
            const dateStr = this.story.approved_at || '';
            const poEmail = this.story.approved_by_email || 'Product Owner';
            logText = `Aprobada por <strong>${escapeHTML(poEmail)}</strong> el ${dateStr}`;
        } else if (appStatus === 'REJECTED') {
            statusText = 'Rechazada';
            statusColor = '#fca5a5';
            statusIcon = '❌';
            const dateStr = this.story.approved_at || '';
            const poEmail = this.story.approved_by_email || 'Product Owner';
            logText = `Rechazada por <strong>${escapeHTML(poEmail)}</strong> el ${dateStr}`;
        } else if (appStatus === 'CHANGES_REQUESTED') {
            statusText = 'Ajustes Solicitados';
            statusColor = '#fdba74';
            statusIcon = '⚠️';
            const dateStr = this.story.approved_at || '';
            const poEmail = this.story.approved_by_email || 'Product Owner';
            logText = `Ajustes solicitados por <strong>${escapeHTML(poEmail)}</strong> el ${dateStr}`;
        }

        const approvalStatusBox = `
            <div style="background: rgba(255, 255, 255, 0.01); border: 1px solid rgba(255, 255, 255, 0.03); border-radius: 12px; padding: 16px; display: flex; flex-direction: column; gap: 8px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 16px;">${statusIcon}</span>
                    <h4 style="font-size: 14px; font-weight: 600; margin: 0; color: var(--text-main);">Estado: <span style="color: ${statusColor};">${statusText}</span></h4>
                </div>
                ${logText ? `<div style="font-size: 11px; color: var(--text-muted);">${logText}</div>` : ''}
                
                ${(appStatus === 'REJECTED' || appStatus === 'CHANGES_REQUESTED') && this.story.rejection_reason ? `
                    <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 8px; padding: 10px 12px; font-size: 12px; color: #fca5a5; margin-top: 4px; line-height: 1.5;">
                        <strong>Motivo / Cambios solicitados:</strong><br>
                        ${escapeHTML(this.story.rejection_reason)}
                    </div>
                ` : ''}
            </div>
        `;

        let actionButtonsHtml = '';
        if (this.userRole === 'PO') {
            actionButtonsHtml = `
                <div style="background: rgba(255, 255, 255, 0.01); border: 1px solid rgba(255, 255, 255, 0.03); border-radius: 12px; padding: 16px; display: flex; flex-direction: column; gap: 12px;">
                    <h4 style="font-size: 14px; font-weight: 600; margin: 0; color: var(--text-main);">Validación del Product Owner</h4>
                    <div style="display: flex; gap: 8px;">
                        <button id="btn-approve-story" class="btn btn-accent btn-sm" style="flex-grow: 1; padding: 8px; font-size: 12px; background: #10b981; box-shadow: none; border-radius: 8px; border: none; height: 32px; width: auto; font-family: inherit;">Aprobar</button>
                        <button id="btn-show-reject" class="btn btn-outline btn-sm" style="flex-grow: 1; padding: 8px; font-size: 12px; border-color: rgba(239, 68, 68, 0.3); color: #fca5a5; border-radius: 8px; height: 32px; width: auto; font-family: inherit;">Rechazar</button>
                        <button id="btn-show-changes" class="btn btn-outline btn-sm" style="flex-grow: 1; padding: 8px; font-size: 12px; border-color: rgba(249, 115, 22, 0.3); color: #fdba74; border-radius: 8px; height: 32px; width: auto; font-family: inherit;">Ajustes</button>
                    </div>

                    <!-- Input form for rejection / changes reasons -->
                    <div id="rejection-form-container" style="display: none; flex-direction: column; gap: 8px; margin-top: 8px; animation: fadeIn 0.2s ease-out;">
                        <label for="rejection-reason-input" id="rejection-form-label" style="font-size: 11px; color: var(--text-muted);">Especifica el motivo *</label>
                        <textarea id="rejection-reason-input" class="form-control" placeholder="Escribe el motivo de la decisión aquí..." style="padding: 8px; font-size: 12px; height: 60px; resize: vertical; margin-bottom: 0; background: rgba(255,255,255,0.02);"></textarea>
                        <div style="display: flex; gap: 6px; align-self: flex-end;">
                            <button id="btn-cancel-rejection" class="btn btn-outline btn-sm" style="padding: 4px 10px; font-size: 11px; width: auto; border-radius: 6px; height: 26px; font-family: inherit;">Cancelar</button>
                            <button id="btn-submit-rejection" class="btn btn-accent btn-sm" style="padding: 4px 10px; font-size: 11px; width: auto; background: var(--accent); border-radius: 6px; height: 26px; font-family: inherit;">Enviar</button>
                        </div>
                    </div>
                </div>
            `;
        } else {
            actionButtonsHtml = `
                <div style="background: rgba(255, 255, 255, 0.01); border: 1px solid rgba(255, 255, 255, 0.03); border-radius: 12px; padding: 14px 16px; font-size: 12px; color: var(--text-muted); text-align: center; border-left: 3px solid var(--accent);">
                    🔒 Sólo los usuarios con rol de <strong>Product Owner</strong> pueden aprobar o rechazar esta historia.
                </div>
            `;
        }

        detailEl.innerHTML = `
            <!-- Back Button -->
            <button id="btn-back-to-stories" style="background: transparent; border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; color: var(--text-muted); padding: 8px 12px; font-size: 12px; cursor: pointer; align-self: flex-start; transition: all 0.2s;" onmouseover="this.style.borderColor='rgba(255,255,255,0.2)'; this.style.color='var(--text-main)'" onmouseout="this.style.borderColor='rgba(255,255,255,0.1)'; this.style.color='var(--text-muted)'">
                ← Volver al listado
            </button>

            <!-- Approval Status Display -->
            ${approvalStatusBox}

            <!-- Validation Action Buttons -->
            ${actionButtonsHtml}

            <!-- Progress Bar Card -->
            <div style="background: rgba(255, 255, 255, 0.01); border: 1px solid rgba(255, 255, 255, 0.03); border-radius: 12px; padding: 16px; display: flex; flex-direction: column; gap: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4 style="font-size: 14px; font-weight: 600; margin: 0; color: var(--text-main);">Progreso de Subtareas</h4>
                    <span style="font-size: 13px; font-weight: 700; color: var(--accent);">${progressPercent}%</span>
                </div>
                <div style="height: 8px; background: rgba(255, 255, 255, 0.05); border-radius: 4px; overflow: hidden;">
                    <div style="height: 100%; width: ${progressPercent}%; background: linear-gradient(90deg, #8b5cf6, #ec4899); border-radius: 4px; transition: width 0.3s ease;"></div>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 11px; color: var(--text-muted); margin-top: 2px;">
                    <span>${completedTasks} de ${totalTasks} completadas</span>
                    <span>Total estimado: ⏱ ${totalHours}h</span>
                </div>
            </div>

            <!-- Technical Subtasks Manager -->
            <div style="display: flex; flex-direction: column; gap: 12px; background: rgba(255, 255, 255, 0.01); border: 1px solid rgba(255, 255, 255, 0.03); border-radius: 12px; padding: 20px;">
                <h4 style="font-size: 14px; font-weight: 600; border-bottom: 1px solid rgba(255, 255, 255, 0.05); padding-bottom: 8px;">Subtareas Técnicas</h4>
                
                <!-- Inline Create Form -->
                <form id="create-task-form" style="display: flex; gap: 8px; align-items: flex-end; background: rgba(255,255,255,0.01); border: 1px solid rgba(255,255,255,0.04); border-radius: 8px; padding: 12px; margin-bottom: 8px;">
                    <div style="flex-grow: 1; display: flex; flex-direction: column; gap: 4px;">
                        <label for="new-task-title" style="font-size: 10px; color: var(--text-muted);">Nueva Subtarea *</label>
                        <input type="text" id="new-task-title" class="form-control" placeholder="Ej. Crear modelo de datos" required style="padding: 6px 12px; font-size: 12px; background: rgba(255,255,255,0.02); height: 32px; margin-bottom: 0;">
                    </div>
                    <div style="width: 80px; display: flex; flex-direction: column; gap: 4px;">
                        <label for="new-task-hours" style="font-size: 10px; color: var(--text-muted);">Horas</label>
                        <input type="number" id="new-task-hours" class="form-control" value="0" min="0" required style="padding: 6px 12px; font-size: 12px; background: rgba(255,255,255,0.02); height: 32px; margin-bottom: 0;">
                    </div>
                    <button type="submit" class="btn btn-accent btn-sm" style="padding: 0 12px; font-size: 12px; height: 32px; width: auto; white-space: nowrap; display: flex; align-items: center; justify-content: center; font-family: inherit;">Agregar</button>
                </form>

                <div id="task-error-alert" class="alert alert-error" style="display: none; font-size: 11px; padding: 8px; margin-bottom: 8px;"></div>

                <div id="tasks-list" style="display: flex; flex-direction: column; gap: 8px;">
                    ${tasksListHtml}
                </div>
            </div>

            <!-- Edit Story Form -->
            <form id="edit-story-form" style="display: flex; flex-direction: column; gap: 16px; background: rgba(255, 255, 255, 0.01); border: 1px solid rgba(255, 255, 255, 0.03); border-radius: 12px; padding: 20px;">
                <h4 style="font-size: 15px; font-weight: 600; border-bottom: 1px solid rgba(255, 255, 255, 0.05); padding-bottom: 8px;">Editar Historia de Usuario</h4>
                
                <div class="form-group" style="margin-bottom: 0;">
                    <label class="form-label" for="edit-story-title" style="font-size: 11px;">Título *</label>
                    <input class="form-control" type="text" id="edit-story-title" value="${escapeHTML(this.story.title)}" required style="padding: 8px 12px; font-size: 13px;">
                </div>

                <div class="form-group" style="margin-bottom: 0;">
                    <label class="form-label" for="edit-story-desc" style="font-size: 11px;">Descripción</label>
                    <textarea class="form-control" id="edit-story-desc" style="padding: 8px 12px; font-size: 13px; height: 60px; resize: vertical;">${escapeHTML(this.story.description || '')}</textarea>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                    <div class="form-group" style="margin-bottom: 0;">
                        <label class="form-label" for="edit-story-priority" style="font-size: 11px;">Prioridad</label>
                        <select class="form-control" id="edit-story-priority" style="padding: 8px 12px; font-size: 13px;">
                            <option value="LOW" ${this.story.priority === 'LOW' ? 'selected' : ''}>Baja</option>
                            <option value="MEDIUM" ${this.story.priority === 'MEDIUM' ? 'selected' : ''}>Media</option>
                            <option value="HIGH" ${this.story.priority === 'HIGH' ? 'selected' : ''}>Alta</option>
                        </select>
                    </div>

                    <div class="form-group" style="margin-bottom: 0;">
                        <label class="form-label" for="edit-story-value" style="font-size: 11px;">Valor de Negocio</label>
                        <input class="form-control" type="number" id="edit-story-value" value="${this.story.business_value}" min="0" required style="padding: 8px 12px; font-size: 13px;">
                    </div>
                </div>

                <div class="form-group" style="margin-bottom: 0;">
                    <label class="form-label" for="edit-story-status" style="font-size: 11px;">Estado</label>
                    <select class="form-control" id="edit-story-status" style="padding: 8px 12px; font-size: 13px;">
                        <option value="ACTIVE" ${this.story.status === 'ACTIVE' ? 'selected' : ''}>Activa</option>
                        <option value="COMPLETED" ${this.story.status === 'COMPLETED' ? 'selected' : ''}>Completada</option>
                        <option value="ARCHIVED" ${this.story.status === 'ARCHIVED' ? 'selected' : ''}>Archivada</option>
                    </select>
                </div>

                <button type="submit" class="btn btn-accent" id="btn-update-story" style="padding: 8px 16px; font-size: 13px;">Actualizar Historia</button>
            </form>

            <!-- Linked Tasks Block -->
            <div style="display: flex; flex-direction: column; gap: 12px;">
                <h4 style="font-size: 14px; font-weight: 600;">Tareas Vinculadas (${this.story.cards.length})</h4>
                
                <!-- Link New Card Inline -->
                ${linkableCards.length > 0 ? `
                    <div style="display: flex; gap: 8px; align-items: center; background: rgba(255,255,255,0.01); border: 1px solid rgba(255,255,255,0.04); border-radius: 8px; padding: 12px;">
                        <select id="select-link-card" class="form-control" style="flex-grow: 1; padding: 6px 12px; font-size: 12px; height: 32px; margin-bottom: 0;">
                            ${linkableOptions}
                        </select>
                        <button id="btn-link-card-submit" class="btn btn-accent btn-sm" style="padding: 0 12px; font-size: 12px; height: 32px; width: auto; white-space: nowrap; font-family: inherit;">+ Vincular</button>
                    </div>
                ` : ''}

                <div id="linked-cards-list" style="display: flex; flex-direction: column; gap: 8px;">
                    ${linkedCardsHtml}
                </div>
            </div>
        `;

        // Event listener hooks
        const backBtn = detailEl.querySelector('#btn-back-to-stories');
        const editForm = detailEl.querySelector('#edit-story-form');
        const linkBtn = detailEl.querySelector('#btn-link-card-submit');
        const unlinkButtons = detailEl.querySelectorAll('.btn-unlink-card');

        // Task Action Hooks
        const createTaskForm = detailEl.querySelector('#create-task-form');
        const statusSelects = detailEl.querySelectorAll('.select-task-status');
        const deleteTaskBtns = detailEl.querySelectorAll('.btn-delete-task');

        // Validation Action Hooks
        const approveBtn = detailEl.querySelector('#btn-approve-story');
        const showRejectBtn = detailEl.querySelector('#btn-show-reject');
        const showChangesBtn = detailEl.querySelector('#btn-show-changes');
        const rejectionContainer = detailEl.querySelector('#rejection-form-container');
        const rejectionInput = detailEl.querySelector('#rejection-reason-input');
        const rejectionLabel = detailEl.querySelector('#rejection-form-label');
        const cancelRejectionBtn = detailEl.querySelector('#btn-cancel-rejection');
        const submitRejectionBtn = detailEl.querySelector('#btn-submit-rejection');

        if (backBtn) {
            backBtn.addEventListener('click', () => {
                if (typeof this.onBack === 'function') {
                    this.onBack();
                }
            });
        }

        if (editForm) {
            editForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const title = editForm.querySelector('#edit-story-title').value;
                const description = editForm.querySelector('#edit-story-desc').value;
                const priority = editForm.querySelector('#edit-story-priority').value;
                const business_value = parseInt(editForm.querySelector('#edit-story-value').value || 0);
                const status = editForm.querySelector('#edit-story-status').value;

                if (typeof this.onUpdate === 'function') {
                    this.onUpdate({
                        story_id: this.story.id,
                        title,
                        description,
                        priority,
                        business_value,
                        status
                    });
                }
            });
        }

        if (linkBtn) {
            linkBtn.addEventListener('click', () => {
                const selectEl = detailEl.querySelector('#select-link-card');
                const cardId = parseInt(selectEl.value);
                if (cardId && typeof this.onLinkCard === 'function') {
                    this.onLinkCard(cardId, this.story.id);
                }
            });
        }

        unlinkButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const cardId = parseInt(btn.getAttribute('data-card-id'));
                if (cardId && typeof this.onUnlinkCard === 'function') {
                    this.onUnlinkCard(cardId, this.story.id);
                }
            });
        });

        // Technical subtask form submit listener
        if (createTaskForm) {
            createTaskForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const titleInput = createTaskForm.querySelector('#new-task-title');
                const hoursInput = createTaskForm.querySelector('#new-task-hours');
                const errorAlert = detailEl.querySelector('#task-error-alert');

                const title = titleInput.value ? titleInput.value.trim() : '';
                const hours = parseInt(hoursInput.value || 0);

                errorAlert.style.display = 'none';

                if (typeof this.onCreateTask === 'function') {
                    try {
                        await this.onCreateTask(title, hours);
                        titleInput.value = '';
                        hoursInput.value = '0';
                    } catch (err) {
                        errorAlert.innerText = err.message || 'Error al crear la subtarea.';
                        errorAlert.style.display = 'block';
                    }
                }
            });
        }

        // Technical subtasks status dropdown listeners
        statusSelects.forEach(select => {
            select.addEventListener('change', async () => {
                const taskId = parseInt(select.getAttribute('data-task-id'));
                const status = select.value;
                const task = this.story.tasks.find(t => t.id === taskId);
                if (task && typeof this.onUpdateTask === 'function') {
                    try {
                        await this.onUpdateTask(taskId, {
                            title: task.title,
                            description: task.description,
                            estimated_hours: task.estimated_hours,
                            status: status
                        });
                    } catch (err) {
                        alert(err.message || 'Error al actualizar el estado de la tarea.');
                        select.value = task.status; // Revert selection
                    }
                }
            });
        });

        // Technical subtasks delete buttons listeners
        deleteTaskBtns.forEach(btn => {
            btn.addEventListener('click', async () => {
                const taskId = parseInt(btn.getAttribute('data-task-id'));
                if (taskId && confirm('¿Estás seguro de que deseas eliminar esta subtarea técnica?')) {
                    if (typeof this.onDeleteTask === 'function') {
                        try {
                            await this.onDeleteTask(taskId);
                        } catch (err) {
                            alert(err.message || 'Error al eliminar la subtarea.');
                        }
                    }
                }
            });
        });

        // Validation buttons wiring
        if (approveBtn) {
            approveBtn.addEventListener('click', async () => {
                if (confirm('¿Estás seguro de que deseas aprobar esta historia de usuario?')) {
                    if (typeof this.onApprove === 'function') {
                        try {
                            await this.onApprove();
                        } catch (err) {
                            alert(err.message || 'Error al aprobar la historia.');
                        }
                    }
                }
            });
        }

        let pendingAction = ''; // 'reject' or 'changes'

        if (showRejectBtn) {
            showRejectBtn.addEventListener('click', () => {
                rejectionContainer.style.display = 'flex';
                rejectionLabel.innerText = 'Especifica el motivo de rechazo *';
                rejectionInput.placeholder = 'Ej. No cumple con las especificaciones de diseño.';
                pendingAction = 'reject';
                rejectionInput.focus();
            });
        }

        if (showChangesBtn) {
            showChangesBtn.addEventListener('click', () => {
                rejectionContainer.style.display = 'flex';
                rejectionLabel.innerText = 'Especifica los cambios requeridos *';
                rejectionInput.placeholder = 'Ej. Añadir criterios de aceptación detallados.';
                pendingAction = 'changes';
                rejectionInput.focus();
            });
        }

        if (cancelRejectionBtn) {
            cancelRejectionBtn.addEventListener('click', () => {
                rejectionContainer.style.display = 'none';
                rejectionInput.value = '';
                pendingAction = '';
            });
        }

        if (submitRejectionBtn) {
            submitRejectionBtn.addEventListener('click', async () => {
                const reason = rejectionInput.value.trim();
                if (!reason) {
                    alert('Por favor especifica un motivo.');
                    return;
                }

                if (pendingAction === 'reject') {
                    if (typeof this.onReject === 'function') {
                        try {
                            await this.onReject(reason);
                            rejectionContainer.style.display = 'none';
                            rejectionInput.value = '';
                        } catch (err) {
                            alert(err.message || 'Error al rechazar la historia.');
                        }
                    }
                } else if (pendingAction === 'changes') {
                    if (typeof this.onRequestChanges === 'function') {
                        try {
                            await this.onRequestChanges(reason);
                            rejectionContainer.style.display = 'none';
                            rejectionInput.value = '';
                        } catch (err) {
                            alert(err.message || 'Error al solicitar cambios.');
                        }
                    }
                }
            });
        }

        return detailEl;
    }
}

class StoryList {
    /**
     * @param {HTMLElement|string} container - HTML target container
     * @param {number} boardId - Active board ID
     * @param {string} csrfToken - Security CSRF token
     */
    constructor(container, boardId, csrfToken) {
        this.container = typeof container === 'string' ? document.getElementById(container) : container;
        this.boardId = boardId;
        this.csrfToken = csrfToken;
        this.stories = [];
        this.userRole = 'DEV'; // Default active role
        this.viewMode = 'list'; // 'list', 'create', 'detail'
        this.activeStoryId = null;
    }

    async load() {
        this.container.innerHTML = `<div style="text-align:center; padding:20px; color:var(--text-muted); font-size:13px;">Cargando historias...</div>`;
        try {
            const response = await fetch(`/stories/boards/${this.boardId}`);
            const data = await response.json();
            if (data.status === 'success') {
                this.stories = data.stories || [];
                this.userRole = data.user_role || 'DEV';
                this.render();
            } else {
                this.container.innerHTML = `<div style="padding:20px; color:#fca5a5; font-size:12px;">Error al cargar historias: ${data.message}</div>`;
            }
        } catch (e) {
            this.container.innerHTML = `<div style="padding:20px; color:#fca5a5; font-size:12px;">Error de conexión.</div>`;
        }
    }

    render() {
        if (!this.container) return;
        this.container.innerHTML = '';

        // Render global role simulator header
        const roleHeader = document.createElement('div');
        roleHeader.style.cssText = `
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 10px 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
            margin-bottom: 16px;
            animation: fadeIn 0.3s ease-out forwards;
        `;
        const activeRoleName = (this.userRole === 'PO') ? 'Product Owner 👑' : 'Developer 💻';
        roleHeader.innerHTML = `
            <span style="color: var(--text-muted);">Rol simulado: <strong style="color: var(--text-main);">${activeRoleName}</strong></span>
            <button id="btn-toggle-role" class="btn btn-accent btn-sm" style="padding: 4px 10px; font-size: 11px; width: auto; background: var(--accent); border-radius: 6px; box-shadow: none; height: 24px; font-family: inherit;">Cambiar Rol</button>
        `;
        
        roleHeader.querySelector('#btn-toggle-role').addEventListener('click', async () => {
            try {
                const response = await fetch('/stories/toggle-role', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.csrfToken
                    }
                });
                const data = await response.json();
                if (data.status === 'success') {
                    this.userRole = data.role;
                    // Reload current view
                    if (this.viewMode === 'detail') {
                        await this.renderDetailView();
                    } else if (this.viewMode === 'list') {
                        await this.load();
                    } else {
                        this.render();
                    }
                } else {
                    alert(data.message || 'Error al cambiar de rol.');
                }
            } catch (e) {
                alert('Error de conexión.');
            }
        });

        this.container.appendChild(roleHeader);

        // Render inner content container
        const contentEl = document.createElement('div');
        contentEl.id = 'stories-inner-content';
        this.container.appendChild(contentEl);

        if (this.viewMode === 'create') {
            this.renderCreateForm(contentEl);
        } else if (this.viewMode === 'detail') {
            this.renderDetailView(contentEl);
        } else {
            this.renderListView(contentEl);
        }
    }

    renderListView(contentEl) {
        const header = document.createElement('div');
        header.style.cssText = `
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        `;
        header.innerHTML = `
            <h3 style="font-size: 18px; font-weight: 700; color: var(--text-main);">Historias de Usuario</h3>
            <button id="btn-open-create-story" class="btn btn-accent btn-sm" style="padding: 6px 12px; font-size: 12px; width: auto;">+ Nueva</button>
        `;

        contentEl.appendChild(header);

        const listContainer = document.createElement('div');
        listContainer.style.cssText = `
            display: flex;
            flex-direction: column;
            gap: 12px;
            overflow-y: auto;
            max-height: calc(100vh - 220px);
            padding-bottom: 20px;
        `;

        if (this.stories.length === 0) {
            listContainer.innerHTML = `
                <div style="text-align: center; padding: 40px 20px; border: 1px dashed rgba(255,255,255,0.06); border-radius: 12px; color: var(--text-muted); font-size: 13px;">
                    Aún no hay historias de usuario en este tablero. ¡Define los requisitos de negocio creando la primera!
                </div>
            `;
        } else {
            this.stories.forEach(story => {
                const cardComp = new StoryCard(story, (id) => {
                    this.viewMode = 'detail';
                    this.activeStoryId = id;
                    this.render();
                });
                listContainer.appendChild(cardComp.render());
            });
        }

        contentEl.appendChild(listContainer);

        // Bind create button
        const createBtn = header.querySelector('#btn-open-create-story');
        if (createBtn) {
            createBtn.addEventListener('click', () => {
                this.viewMode = 'create';
                this.render();
            });
        }
    }

    renderCreateForm(contentEl) {
        const createEl = document.createElement('div');
        createEl.style.cssText = `
            display: flex;
            flex-direction: column;
            gap: 16px;
            animation: fadeIn 0.3s ease-out forwards;
        `;

        createEl.innerHTML = `
            <button id="btn-cancel-create" style="background: transparent; border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; color: var(--text-muted); padding: 8px 12px; font-size: 12px; cursor: pointer; align-self: flex-start; transition: all 0.2s;" onmouseover="this.style.borderColor='rgba(255,255,255,0.2)'; this.style.color='var(--text-main)'" onmouseout="this.style.borderColor='rgba(255,255,255,0.1)'; this.style.color='var(--text-muted)'">
                ← Cancelar
            </button>

            <form id="create-story-form" style="display: flex; flex-direction: column; gap: 16px; background: rgba(255,255,255,0.01); border: 1px solid rgba(255,255,255,0.03); border-radius: 12px; padding: 20px;">
                <h4 style="font-size: 15px; font-weight: 600; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 8px; color: var(--text-main);">Nueva Historia de Usuario</h4>
                
                <div class="alert alert-error" id="story-form-error" style="display:none; font-size:12px; padding:10px; margin-bottom:0;"></div>

                <div class="form-group" style="margin-bottom: 0;">
                    <label class="form-label" for="story-title" style="font-size: 11px;">Título *</label>
                    <input class="form-control" type="text" id="story-title" placeholder="Ej. Autenticación con OAuth" required style="padding: 8px 12px; font-size: 13px;">
                </div>

                <div class="form-group" style="margin-bottom: 0;">
                    <label class="form-label" for="story-desc" style="font-size: 11px;">Descripción</label>
                    <textarea class="form-control" id="story-desc" placeholder="Como usuario, quiero iniciar sesión..." style="padding: 8px 12px; font-size: 13px; height: 80px; resize: vertical;"></textarea>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                    <div class="form-group" style="margin-bottom: 0;">
                        <label class="form-label" for="story-priority" style="font-size: 11px;">Prioridad</label>
                        <select class="form-control" id="story-priority" style="padding: 8px 12px; font-size: 13px;">
                            <option value="LOW">Baja</option>
                            <option value="MEDIUM" selected>Media</option>
                            <option value="HIGH">Alta</option>
                        </select>
                    </div>

                    <div class="form-group" style="margin-bottom: 0;">
                        <label class="form-label" for="story-value" style="font-size: 11px;">Valor de Negocio</label>
                        <input class="form-control" type="number" id="story-value" value="0" min="0" required style="padding: 8px 12px; font-size: 13px;">
                    </div>
                </div>

                <button type="submit" class="btn btn-accent" id="btn-save-story" style="padding: 10px; font-size: 13px;">Crear Historia</button>
            </form>
        `;

        contentEl.appendChild(createEl);

        const cancelBtn = createEl.querySelector('#btn-cancel-create');
        const form = createEl.querySelector('#create-story-form');

        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                this.viewMode = 'list';
                this.render();
            });
        }

        if (form) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const title = form.querySelector('#story-title').value;
                const description = form.querySelector('#story-desc').value;
                const priority = form.querySelector('#story-priority').value;
                const business_value = parseInt(form.querySelector('#story-value').value || 0);
                const submitBtn = form.querySelector('#btn-save-story');
                const errAlert = form.querySelector('#story-form-error');

                submitBtn.disabled = true;
                submitBtn.innerText = 'Guardando...';
                errAlert.style.display = 'none';

                try {
                    const response = await fetch('/stories/create', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': this.csrfToken
                        },
                        body: JSON.stringify({
                            board_id: this.boardId,
                            title,
                            description,
                            priority,
                            business_value
                        })
                    });

                    const data = await response.json();
                    if (response.ok && data.status === 'success') {
                        this.viewMode = 'list';
                        await this.load();
                    } else {
                        errAlert.innerText = data.message || 'Error al crear la historia.';
                        errAlert.style.display = 'block';
                    }
                } catch (err) {
                    errAlert.innerText = 'Error de conexión con el servidor.';
                    errAlert.style.display = 'block';
                } finally {
                    submitBtn.disabled = false;
                    submitBtn.innerText = 'Crear Historia';
                }
            });
        }
    }

    async renderDetailView(contentEl) {
        if (!contentEl) {
            contentEl = this.container.querySelector('#stories-inner-content');
        }
        contentEl.innerHTML = `<div style="text-align:center; padding:20px; color:var(--text-muted); font-size:13px;">Cargando detalle...</div>`;
        try {
            const response = await fetch(`/stories/${this.activeStoryId}`);
            const data = await response.json();
            if (data.status === 'success') {
                const story = data.story;
                contentEl.innerHTML = '';
                this.userRole = data.user_role || 'DEV';
                
                const detailComp = new StoryDetail(
                    story,
                    this.userRole,
                    () => {
                        this.viewMode = 'list';
                        this.activeStoryId = null;
                        this.render();
                    },
                    (updatedData) => this.handleUpdateStory(updatedData),
                    (cardId, storyId) => this.handleLinkCard(cardId, storyId),
                    (cardId, storyId) => this.handleUnlinkCard(cardId, storyId),
                    (title, hours) => this.handleCreateTask(title, hours),
                    (taskId, payload) => this.handleUpdateTask(taskId, payload),
                    (taskId) => this.handleDeleteTask(taskId),
                    () => this.handleApproveStory(),
                    (reason) => this.handleRejectStory(reason),
                    (reason) => this.handleRequestChanges(reason)
                );

                contentEl.appendChild(detailComp.render());
            } else {
                contentEl.innerHTML = `<div style="padding:20px; color:#fca5a5; font-size:12px;">Error al cargar detalle: ${data.message}</div>`;
            }
        } catch (e) {
            contentEl.innerHTML = `<div style="padding:20px; color:#fca5a5; font-size:12px;">Error de conexión.</div>`;
        }
    }

    async handleUpdateStory(payload) {
        try {
            const response = await fetch('/stories/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();
            if (response.ok && data.status === 'success') {
                await this.renderDetailView();
            } else {
                alert(data.message || 'Error al actualizar la historia.');
            }
        } catch (e) {
            alert('Error de conexión.');
        }
    }

    async handleLinkCard(cardId, storyId) {
        try {
            const response = await fetch('/stories/link', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({ card_id: cardId, story_id: storyId })
            });

            const data = await response.json();
            if (response.ok && data.status === 'success') {
                await this.renderDetailView();
                if (window.fetchColumns) {
                    await window.fetchColumns();
                }
            } else {
                alert(data.message || 'Error al vincular la tarea.');
            }
        } catch (e) {
            alert('Error de conexión.');
        }
    }

    async handleUnlinkCard(cardId, storyId) {
        try {
            const response = await fetch('/stories/link', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({ card_id: cardId, story_id: null })
            });

            const data = await response.json();
            if (response.ok && data.status === 'success') {
                await this.renderDetailView();
                if (window.fetchColumns) {
                    await window.fetchColumns();
                }
            } else {
                alert(data.message || 'Error al desvincular la tarea.');
            }
        } catch (e) {
            alert('Error de conexión.');
        }
    }

    async handleCreateTask(title, estimatedHours) {
        try {
            const response = await fetch('/tasks/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({
                    story_id: this.activeStoryId,
                    title: title,
                    estimated_hours: estimatedHours,
                    status: 'TODO'
                })
            });

            const data = await response.json();
            if (response.ok && data.status === 'success') {
                await this.load();
                await this.renderDetailView();
            } else {
                throw new Error(data.message || 'Error al crear la subtarea.');
            }
        } catch (e) {
            throw e;
        }
    }

    async handleUpdateTask(taskId, payload) {
        try {
            const response = await fetch('/tasks/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({
                    task_id: taskId,
                    title: payload.title,
                    description: payload.description,
                    estimated_hours: payload.estimated_hours,
                    status: payload.status
                })
            });

            const data = await response.json();
            if (response.ok && data.status === 'success') {
                await this.load();
                await this.renderDetailView();
            } else {
                throw new Error(data.message || 'Error al actualizar la subtarea.');
            }
        } catch (e) {
            throw e;
        }
    }

    async handleDeleteTask(taskId) {
        try {
            const response = await fetch('/tasks/delete', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({
                    task_id: taskId
                })
            });

            const data = await response.json();
            if (response.ok && data.status === 'success') {
                await this.load();
                await this.renderDetailView();
            } else {
                throw new Error(data.message || 'Error al eliminar la subtarea.');
            }
        } catch (e) {
            throw e;
        }
    }

    async handleApproveStory() {
        try {
            const response = await fetch(`/stories/${this.activeStoryId}/approve`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                }
            });

            const data = await response.json();
            if (response.ok && data.status === 'success') {
                await this.load();
                await this.renderDetailView();
            } else {
                throw new Error(data.message || 'Error al aprobar la historia.');
            }
        } catch (e) {
            throw e;
        }
    }

    async handleRejectStory(reason) {
        try {
            const response = await fetch(`/stories/${this.activeStoryId}/reject`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({ reason: reason })
            });

            const data = await response.json();
            if (response.ok && data.status === 'success') {
                await this.load();
                await this.renderDetailView();
            } else {
                throw new Error(data.message || 'Error al rechazar la historia.');
            }
        } catch (e) {
            throw e;
        }
    }

    async handleRequestChanges(reason) {
        try {
            const response = await fetch(`/stories/${this.activeStoryId}/request-changes`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({ reason: reason })
            });

            const data = await response.json();
            if (response.ok && data.status === 'success') {
                await this.load();
                await this.renderDetailView();
            } else {
                throw new Error(data.message || 'Error al solicitar ajustes.');
            }
        } catch (e) {
            throw e;
        }
    }
}

// Export to global scope
window.StoryList = StoryList;
