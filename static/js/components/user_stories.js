// Reusable Frontend Components for Organa User Stories

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

        const value = this.story.business_value || 0;
        const title = escapeHTML(this.story.title);
        const desc = escapeHTML(this.story.description || '');

        cardEl.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; gap: 6px;">
                <span style="font-size: 10px; font-weight: 600; padding: 2px 8px; border-radius: 8px; background: ${priBg}; color: ${priColor}; border: ${priBorder}; text-transform: uppercase;">
                    ${priLabel}
                </span>
                <div style="display: flex; gap: 6px;">
                    <span style="font-size: 10px; font-weight: 600; padding: 2px 8px; border-radius: 8px; background: ${statBg}; color: ${statColor}; border: 1px solid ${statColor}30;">
                        ${statLabel}
                    </span>
                    <span style="font-size: 10px; font-weight: 600; padding: 2px 8px; border-radius: 8px; background: rgba(139, 92, 246, 0.12); color: #d8b4fe; border: 1px solid rgba(139, 92, 246, 0.25);">
                        Valor: ${value}
                    </span>
                </div>
            </div>
            <h4 style="font-size: 14px; font-weight: 600; color: var(--text-main); margin: 0; line-height: 1.4;">${title}</h4>
            ${desc ? `<p style="font-size: 12px; color: var(--text-muted); margin: 0; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; line-height: 1.5;">${desc}</p>` : ''}
            
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
     * @param {Function} onBack - Callback to return to list view
     * @param {Function} onUpdate - Callback to update story attributes
     * @param {Function} onLinkCard - Callback to link a card
     * @param {Function} onUnlinkCard - Callback to unlink a card
     */
    constructor(story, onBack, onUpdate, onLinkCard, onUnlinkCard) {
        this.story = story;
        this.onBack = onBack;
        this.onUpdate = onUpdate;
        this.onLinkCard = onLinkCard;
        this.onUnlinkCard = onUnlinkCard;
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

        detailEl.innerHTML = `
            <!-- Back Button -->
            <button id="btn-back-to-stories" style="background: transparent; border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; color: var(--text-muted); padding: 8px 12px; font-size: 12px; cursor: pointer; align-self: flex-start; transition: all 0.2s;" onmouseover="this.style.borderColor='rgba(255,255,255,0.2)'; this.style.color='var(--text-main)'" onmouseout="this.style.borderColor='rgba(255,255,255,0.1)'; this.style.color='var(--text-muted)'">
                ← Volver al listado
            </button>

            <!-- Edit Story Form -->
            <form id="edit-story-form" style="display: flex; flex-direction: column; gap: 16px; background: rgba(255,255,255,0.01); border: 1px solid rgba(255,255,255,0.03); border-radius: 12px; padding: 20px;">
                <h4 style="font-size: 15px; font-weight: 600; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 8px;">Editar Historia de Usuario</h4>
                
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
                        <select id="select-link-card" class="form-control" style="flex-grow: 1; padding: 6px 12px; font-size: 12px;">
                            ${linkableOptions}
                        </select>
                        <button id="btn-link-card-submit" class="btn btn-accent btn-sm" style="padding: 6px 12px; font-size: 12px; width: auto; white-space: nowrap;">+ Vincular</button>
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

        if (this.viewMode === 'create') {
            this.renderCreateForm();
        } else if (this.viewMode === 'detail') {
            this.renderDetailView();
        } else {
            this.renderListView();
        }
    }

    renderListView() {
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

        this.container.appendChild(header);

        const listContainer = document.createElement('div');
        listContainer.style.cssText = `
            display: flex;
            flex-direction: column;
            gap: 12px;
            overflow-y: auto;
            max-height: calc(100vh - 180px);
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

        this.container.appendChild(listContainer);

        // Bind create button
        const createBtn = header.querySelector('#btn-open-create-story');
        if (createBtn) {
            createBtn.addEventListener('click', () => {
                this.viewMode = 'create';
                this.render();
            });
        }
    }

    renderCreateForm() {
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

        this.container.appendChild(createEl);

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

    async renderDetailView() {
        this.container.innerHTML = `<div style="text-align:center; padding:20px; color:var(--text-muted); font-size:13px;">Cargando detalle...</div>`;
        try {
            const response = await fetch(`/stories/${this.activeStoryId}`);
            const data = await response.json();
            if (data.status === 'success') {
                const story = data.story;
                this.container.innerHTML = '';
                
                const detailComp = new StoryDetail(
                    story,
                    () => {
                        this.viewMode = 'list';
                        this.activeStoryId = null;
                        this.render();
                    },
                    (updatedData) => this.handleUpdateStory(updatedData),
                    (cardId, storyId) => this.handleLinkCard(cardId, storyId),
                    (cardId, storyId) => this.handleUnlinkCard(cardId, storyId)
                );

                this.container.appendChild(detailComp.render());
            } else {
                this.container.innerHTML = `<div style="padding:20px; color:#fca5a5; font-size:12px;">Error al cargar detalle: ${data.message}</div>`;
            }
        } catch (e) {
            this.container.innerHTML = `<div style="padding:20px; color:#fca5a5; font-size:12px;">Error de conexión.</div>`;
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
                // Return to details view
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
                // Refresh detail view
                await this.renderDetailView();
                // Dynamically reload the card's column to display its story label
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
                // Refresh detail view
                await this.renderDetailView();
                // Dynamically reload the card's column to remove its story label
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
}

// Export to global scope
window.StoryList = StoryList;
