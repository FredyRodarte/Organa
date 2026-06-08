// Organa Kanban Metrics Frontend Component

class MetricsCard {
    constructor(title, value, color) {
        this.title = title;
        this.value = value;
        this.color = color || 'var(--accent)';
    }

    render() {
        const card = document.createElement('div');
        card.className = 'metrics-card';
        card.style.cssText = `
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 14px;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 6px;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            position: relative;
            overflow: hidden;
        `;

        card.addEventListener('mouseenter', () => {
            card.style.background = 'rgba(255, 255, 255, 0.04)';
            card.style.borderColor = 'rgba(99, 102, 241, 0.25)';
            card.style.boxShadow = '0 8px 20px rgba(0, 0, 0, 0.25)';
            card.style.transform = 'translateY(-2px)';
        });
        card.addEventListener('mouseleave', () => {
            card.style.background = 'rgba(255, 255, 255, 0.02)';
            card.style.borderColor = 'rgba(255, 255, 255, 0.05)';
            card.style.boxShadow = 'none';
            card.style.transform = 'none';
        });

        card.innerHTML = `
            <div style="font-size: 11px; font-weight: 500; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px;">${this.title}</div>
            <div style="font-size: 26px; font-weight: 700; color: ${this.color}; line-height: 1.2;">${this.value}</div>
        `;
        return card;
    }
}

class ProgressWidget {
    constructor(percentage, label) {
        this.percentage = percentage;
        this.label = label || 'Avance General';
    }

    render() {
        const widget = document.createElement('div');
        widget.style.cssText = `
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        `;

        const progressColor = `linear-gradient(90deg, #818cf8 0%, #6366f1 100%)`;

        widget.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 13px; font-weight: 600; color: var(--text-main);">${this.label}</span>
                <span style="font-size: 15px; font-weight: 700; color: #a5b4fc;">${this.percentage}%</span>
            </div>
            <div style="width: 100%; height: 10px; background: rgba(255, 255, 255, 0.05); border-radius: 10px; overflow: hidden; border: 1px solid rgba(255, 255, 255, 0.03);">
                <div style="width: ${this.percentage}%; height: 100%; background: ${progressColor}; border-radius: 10px; transition: width 0.6s cubic-bezier(0.16, 1, 0.3, 1);"></div>
            </div>
        `;
        return widget;
    }
}

class ColumnDistributionChart {
    constructor(cardsByColumn) {
        this.cardsByColumn = cardsByColumn || [];
    }

    render() {
        const container = document.createElement('div');
        container.style.cssText = `
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        `;

        container.innerHTML = `<h3 style="font-size: 13px; font-weight: 600; color: var(--text-main); border-bottom: 1px solid rgba(255, 255, 255, 0.05); padding-bottom: 8px; margin: 0;">Distribución por Columna</h3>`;

        const maxCount = Math.max(...this.cardsByColumn.map(c => c.count), 1);

        this.cardsByColumn.forEach(col => {
            const widthPct = (col.count / maxCount) * 100;
            const bar = document.createElement('div');
            bar.style.cssText = `
                display: flex;
                flex-direction: column;
                gap: 6px;
            `;

            bar.innerHTML = `
                <div style="display: flex; justify-content: space-between; font-size: 12px; color: var(--text-muted);">
                    <span>${col.name}</span>
                    <span style="font-weight: 600; color: var(--text-main);">${col.count}</span>
                </div>
                <div style="width: 100%; height: 6px; background: rgba(255, 255, 255, 0.03); border-radius: 4px; overflow: hidden;">
                    <div style="width: ${widthPct}%; height: 100%; background: rgba(99, 102, 241, 0.6); border-radius: 4px; transition: width 0.6s cubic-bezier(0.16, 1, 0.3, 1);"></div>
                </div>
            `;
            container.appendChild(bar);
        });

        return container;
    }
}

class WorkloadList {
    constructor(workloadData) {
        this.workloadData = workloadData || [];
    }

    render() {
        const container = document.createElement('div');
        container.style.cssText = `
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 14px;
        `;

        container.innerHTML = `<h3 style="font-size: 13px; font-weight: 600; color: var(--text-main); border-bottom: 1px solid rgba(255, 255, 255, 0.05); padding-bottom: 8px; margin: 0;">Carga por Desarrollador</h3>`;

        if (this.workloadData.length === 0) {
            const empty = document.createElement('div');
            empty.style.cssText = 'font-size: 12px; color: var(--text-muted); text-align: center; padding: 12px 0;';
            empty.textContent = 'Sin asignaciones activas.';
            container.appendChild(empty);
            return container;
        }

        this.workloadData.forEach(item => {
            const initials = (item.email || item.username || 'U').substring(0, 2).toUpperCase();
            const devRow = document.createElement('div');
            devRow.style.cssText = `
                display: flex;
                justify-content: space-between;
                align-items: center;
                background: rgba(255,255,255,0.01);
                border: 1px solid rgba(255,255,255,0.02);
                border-radius: 10px;
                padding: 8px 12px;
            `;

            devRow.innerHTML = `
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="width: 28px; height: 28px; border-radius: 50%; background: rgba(99, 102, 241, 0.2); border: 1px solid rgba(99, 102, 241, 0.4); display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold; color: #a5b4fc;">
                        ${initials}
                    </div>
                    <span style="font-size: 13px; color: var(--text-main); font-weight: 500; max-width: 240px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                        ${item.email || item.username}
                    </span>
                </div>
                <div style="font-size: 11px; font-weight: 700; color: #818cf8; background: rgba(129, 140, 248, 0.1); border: 1px solid rgba(129, 140, 248, 0.2); padding: 2px 8px; border-radius: 12px;">
                    ${item.count} ${item.count === 1 ? 'tarjeta' : 'tarjetas'}
                </div>
            `;
            container.appendChild(devRow);
        });

        return container;
    }
}

class MetricsGrid {
    constructor(cards) {
        this.cards = cards || [];
    }

    render() {
        const grid = document.createElement('div');
        grid.style.cssText = `
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 16px;
        `;
        this.cards.forEach(c => grid.appendChild(c.render()));
        return grid;
    }
}

class MetricsDrawer {
    constructor(contentContainer, boardId) {
        this.container = typeof contentContainer === 'string' ? document.getElementById(contentContainer) : contentContainer;
        this.boardId = boardId;
    }

    async load() {
        if (!this.container) return;
        this.container.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 200px; color: var(--text-muted); font-size: 14px;">
                Cargando métricas...
            </div>
        `;

        try {
            const [boardRes, storyRes, teamRes] = await Promise.all([
                fetch(`/metrics/board/${this.boardId}`),
                fetch(`/metrics/stories/${this.boardId}`),
                fetch(`/metrics/team/${this.boardId}`)
            ]);

            const boardData = await boardRes.json();
            const storyData = await storyRes.json();
            
            let teamData = null;
            if (teamRes.status === 200) {
                teamData = await teamRes.json();
            }

            if (boardData.status !== 'success' || storyData.status !== 'success') {
                this.container.innerHTML = `<div style="color:#fca5a5; padding: 20px; font-size:13px; text-align:center;">Error al cargar datos de métricas.</div>`;
                return;
            }

            this.container.innerHTML = '';
            const boardMetrics = boardData.metrics;
            const storyMetrics = storyData.metrics;
            const isDeveloper = (window.currentUserRole === 'DEV');

            const titleEl = document.getElementById('metrics-sidebar-title');
            if (titleEl) {
                titleEl.textContent = isDeveloper ? '📊 Métricas Personales' : '📊 Métricas del Tablero';
            }

            // 1. Render KPIs
            const kpiCards = [];
            kpiCards.push(new MetricsCard(isDeveloper ? 'Mis Tarjetas' : 'Total Tarjetas', boardMetrics.total_cards, '#a5b4fc'));
            kpiCards.push(new MetricsCard('Completadas', boardMetrics.completed_cards, '#34d399'));
            kpiCards.push(new MetricsCard('Pendientes', boardMetrics.pending_cards, '#fbbf24'));
            
            if (!isDeveloper) {
                kpiCards.push(new MetricsCard('H.U. Aprobadas', storyMetrics.approved_stories, '#c084fc'));
            } else {
                kpiCards.push(new MetricsCard('Mis H.U. Afectadas', storyMetrics.total_stories, '#c084fc'));
            }

            const grid = new MetricsGrid(kpiCards);
            this.container.appendChild(grid.render());

            // 2. Progress Widget
            const progress = new ProgressWidget(boardMetrics.completion_rate, isDeveloper ? 'Mi Porcentaje de Avance' : 'Porcentaje de Avance');
            this.container.appendChild(progress.render());

            // 3. User Story breakdown (only for SM / PO)
            if (!isDeveloper) {
                const storyBreakdown = document.createElement('div');
                storyBreakdown.style.cssText = `
                    background: rgba(255, 255, 255, 0.02);
                    border: 1px solid rgba(255, 255, 255, 0.05);
                    border-radius: 16px;
                    padding: 20px;
                    display: flex;
                    flex-direction: column;
                    gap: 12px;
                `;
                
                storyBreakdown.innerHTML = `
                    <h3 style="font-size: 13px; font-weight: 600; color: var(--text-main); border-bottom: 1px solid rgba(255, 255, 255, 0.05); padding-bottom: 8px; margin: 0;">Historias de Usuario</h3>
                    <div style="display:flex; justify-content:space-between; font-size:12px; color:var(--text-muted);">
                        <span>Aprobadas:</span> <strong style="color:#34d399;">${storyMetrics.approved_stories}</strong>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-size:12px; color:var(--text-muted);">
                        <span>Pendientes de Aprobación:</span> <strong style="color:#fbbf24;">${storyMetrics.pending_stories}</strong>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-size:12px; color:var(--text-muted);">
                        <span>Ajustes Solicitados:</span> <strong style="color:#a5b4fc;">${storyMetrics.changes_requested_stories}</strong>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-size:12px; color:var(--text-muted);">
                        <span>Rechazadas:</span> <strong style="color:#f87171;">${storyMetrics.rejected_stories}</strong>
                    </div>
                `;
                this.container.appendChild(storyBreakdown);
            }

            // 4. Column Distribution Chart
            if (boardMetrics.cards_by_column && boardMetrics.cards_by_column.length > 0) {
                const chart = new ColumnDistributionChart(boardMetrics.cards_by_column);
                this.container.appendChild(chart.render());
            }

            // 5. Workload list
            if (teamData && teamData.workload) {
                const workload = new WorkloadList(teamData.workload);
                this.container.appendChild(workload.render());
            } else if (isDeveloper) {
                const devWorkloadInfo = document.createElement('div');
                devWorkloadInfo.style.cssText = `
                    background: rgba(255, 255, 255, 0.01);
                    border: 1px dashed rgba(255, 255, 255, 0.05);
                    border-radius: 16px;
                    padding: 16px;
                    text-align: center;
                    font-size: 12px;
                    color: var(--text-muted);
                `;
                devWorkloadInfo.textContent = '🔒 La carga de trabajo del equipo solo está disponible para Scrum Master y Product Owner.';
                this.container.appendChild(devWorkloadInfo);
            }

        } catch (error) {
            this.container.innerHTML = `<div style="color:#fca5a5; padding: 20px; font-size:13px; text-align:center;">Error de conexión con el servidor.</div>`;
        }
    }
}

window.MetricsDrawer = MetricsDrawer;
