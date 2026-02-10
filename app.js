class MapBuilder {
    constructor() {
        this.canvas = document.getElementById('mapCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.elements = [];
        this.history = [];
        this.historyStep = -1;
        this.currentTool = null;
        this.isDrawing = false;
        this.startX = 0;
        this.startY = 0;
        this.selectedElement = null;

        this.initializeCanvas();
        this.attachEventListeners();
        this.resizeCanvasToContainer();
    }

    initializeCanvas() {
        this.resizeCanvasToContainer();
        window.addEventListener('resize', () => this.resizeCanvasToContainer());
    }

    resizeCanvasToContainer() {
        const rect = this.canvas.parentElement.getBoundingClientRect();
        this.canvas.width = rect.width;
        this.canvas.height = rect.height - 50;
        this.redraw();
    }

    attachEventListeners() {
        // Tool buttons
        document.getElementById('addMountains').addEventListener('click', () => this.selectTool('mountains'));
        document.getElementById('addRivers').addEventListener('click', () => this.selectTool('rivers'));
        document.getElementById('addLakes').addEventListener('click', () => this.selectTool('lakes'));
        document.getElementById('addForests').addEventListener('click', () => this.selectTool('forests'));
        document.getElementById('addDeserts').addEventListener('click', () => this.selectTool('deserts'));
        document.getElementById('addCities').addEventListener('click', () => this.selectTool('cities'));
        document.getElementById('addText').addEventListener('click', () => this.selectTool('text'));

        // Canvas events
        this.canvas.addEventListener('mousedown', (e) => this.onMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this.onMouseMove(e));
        this.canvas.addEventListener('mouseup', (e) => this.onMouseUp(e));
        this.canvas.addEventListener('mouseleave', (e) => this.onMouseLeave(e));

        // Save/Load buttons
        document.getElementById('saveBtn').addEventListener('click', () => this.saveMap());
        document.getElementById('exportPngBtn').addEventListener('click', () => this.exportPNG());
        document.getElementById('loadBtn').addEventListener('click', () => this.loadMap());
        document.getElementById('clearBtn').addEventListener('click', () => this.clearAll());
        document.getElementById('undoBtn').addEventListener('click', () => this.undo());
        document.getElementById('redoBtn').addEventListener('click', () => this.redo());
        document.getElementById('deleteSelected').addEventListener('click', () => this.deleteSelected());

        // Size adjustment
        document.getElementById('resizeBtn').addEventListener('click', () => this.resizeCanvasToContainer());

        // File input
        document.getElementById('fileInput').addEventListener('change', (e) => this.handleFileLoad(e));
    }

    selectTool(tool) {
        this.currentTool = tool;
        document.querySelectorAll('.tool-btn').forEach(btn => btn.classList.remove('active'));
        event.target.closest('.tool-btn').classList.add('active');
        this.updateToolStatus();
    }

    updateToolStatus() {
        const toolNames = {
            mountains: 'Montañas',
            rivers: 'Ríos',
            lakes: 'Lagos',
            forests: 'Bosques',
            deserts: 'Desiertos',
            cities: 'Ciudades',
            text: 'Texto'
        };
        document.getElementById('tool-status').textContent = `Herramienta: ${toolNames[this.currentTool] || 'Seleccionar'}`;
    }

    getCoordinates(event) {
        const rect = this.canvas.getBoundingClientRect();
        return {
            x: event.clientX - rect.left,
            y: event.clientY - rect.top
        };
    }

    onMouseDown(event) {
        const coords = this.getCoordinates(event);
        this.startX = coords.x;
        this.startY = coords.y;
        this.isDrawing = true;

        if (this.currentTool === 'rivers') {
            this.elements.push({
                type: 'river',
                points: [{x: coords.x, y: coords.y}],
                color: document.getElementById('colorRivers').value,
                width: 3
            });
        } else if (this.currentTool === 'text') {
            const text = prompt('Ingrese el texto:');
            if (text) {
                this.elements.push({
                    type: 'text',
                    text: text,
                    x: coords.x,
                    y: coords.y,
                    color: '#000',
                    fontSize: 16
                });
                this.saveHistory();
                this.redraw();
            }
            this.isDrawing = false;
        }
    }

    onMouseMove(event) {
        const coords = this.getCoordinates(event);
        document.getElementById('coordinates').textContent = `X: ${Math.round(coords.x)}, Y: ${Math.round(coords.y)}`;

        if (!this.isDrawing || !this.currentTool) return;

        if (this.currentTool === 'rivers' && this.elements.length > 0) {
            const lastElement = this.elements[this.elements.length - 1];
            if (lastElement.type === 'river') {
                lastElement.points.push({x: coords.x, y: coords.y});
                this.redraw();
            }
        }
    }

    onMouseUp(event) {
        if (!this.isDrawing) return;
        this.isDrawing = false;

        const coords = this.getCoordinates(event);
        const width = Math.abs(coords.x - this.startX);
        const height = Math.abs(coords.y - this.startY);
        const x = Math.min(coords.x, this.startX);
        const y = Math.min(coords.y, this.startY);

        if (width > 5 && height > 5) {
            if (this.currentTool === 'mountains') {
                this.elements.push({
                    type: 'mountain',
                    x, y, width, height,
                    color: document.getElementById('colorMountains').value
                });
            } else if (this.currentTool === 'lakes') {
                this.elements.push({
                    type: 'lake',
                    x, y, width, height,
                    color: document.getElementById('colorLakes').value
                });
            } else if (this.currentTool === 'forests') {
                this.elements.push({
                    type: 'forest',
                    x, y, width, height,
                    color: document.getElementById('colorForests').value
                });
            } else if (this.currentTool === 'deserts') {
                this.elements.push({
                    type: 'desert',
                    x, y, width, height,
                    color: document.getElementById('colorDeserts').value
                });
            } else if (this.currentTool === 'cities') {
                this.elements.push({
                    type: 'city',
                    x: this.startX,
                    y: this.startY,
                    color: '#ff0000',
                    radius: 8
                });
            }
            this.saveHistory();
        }

        this.redraw();
    }

    onMouseLeave(event) {
        if (this.isDrawing && this.currentTool === 'rivers') {
            this.isDrawing = false;
            this.saveHistory();
            this.redraw();
        }
    }

    drawElement(element) {
        switch (element.type) {
            case 'mountain':
                this.drawMountain(element);
                break;
            case 'river':
                this.drawRiver(element);
                break;
            case 'lake':
                this.drawLake(element);
                break;
            case 'forest':
                this.drawForest(element);
                break;
            case 'desert':
                this.drawDesert(element);
                break;
            case 'city':
                this.drawCity(element);
                break;
            case 'text':
                this.drawText(element);
                break;
        }
    }

    drawMountain(element) {
        this.ctx.fillStyle = element.color;
        this.ctx.beginPath();
        this.ctx.moveTo(element.x + element.width / 2, element.y);
        this.ctx.lineTo(element.x + element.width, element.y + element.height);
        this.ctx.lineTo(element.x, element.y + element.height);
        this.ctx.closePath();
        this.ctx.fill();
        this.ctx.strokeStyle = '#333';
        this.ctx.lineWidth = 2;
        this.ctx.stroke();
    }

    drawRiver(element) {
        if (element.points.length < 2) return;
        this.ctx.strokeStyle = element.color;
        this.ctx.lineWidth = element.width;
        this.ctx.lineCap = 'round';
        this.ctx.lineJoin = 'round';
        this.ctx.beginPath();
        this.ctx.moveTo(element.points[0].x, element.points[0].y);
        for (let i = 1; i < element.points.length; i++) {
            this.ctx.lineTo(element.points[i].x, element.points[i].y);
        }
        this.ctx.stroke();
    }

    drawLake(element) {
        this.ctx.fillStyle = element.color;
        this.ctx.beginPath();
        this.ctx.ellipse(element.x + element.width / 2, element.y + element.height / 2, element.width / 2, element.height / 2, 0, 0, Math.PI * 2);
        this.ctx.fill();
        this.ctx.strokeStyle = '#333';
        this.ctx.lineWidth = 1;
        this.ctx.stroke();
    }

    drawForest(element) {
        this.ctx.fillStyle = element.color;
        this.ctx.fillRect(element.x, element.y, element.width, element.height);
        for (let i = 0; i < 20; i++) {
            const x = element.x + Math.random() * element.width;
            const y = element.y + Math.random() * element.height;
            this.ctx.fillStyle = '#1a5d1a';
            this.ctx.beginPath();
            this.ctx.arc(x, y, 3, 0, Math.PI * 2);
            this.ctx.fill();
        }
    }

    drawDesert(element) {
        this.ctx.fillStyle = element.color;
        this.ctx.fillRect(element.x, element.y, element.width, element.height);
        for (let i = 0; i < 15; i++) {
            const x = element.x + Math.random() * element.width;
            const y = element.y + Math*
