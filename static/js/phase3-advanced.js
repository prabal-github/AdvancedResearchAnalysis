/**
 * Phase 3: Advanced Features JavaScript
 * Progressive Web App, D3.js Visualizations, Real-time Updates, Mobile Enhancements
 */

class Phase3Manager {
    constructor() {
        this.isOnline = navigator.onLine;
        this.realtimeConnections = new Map();
        this.d3Charts = new Map();
        this.installPrompt = null;
        this.mobileBreakpoint = 768;
        this.init();
    }

    async init() {
        console.log('🚀 Phase 3: Advanced Features Initializing...');
        
        // Initialize core features
        await this.initializePWA();
        this.initializeMobileFirst();
        this.initializeRealtime();
        this.initializeD3Visualizations();
        this.initializeConnectionMonitoring();
        this.initializePerformanceOptimizations();
        
        console.log('✅ Phase 3: All features initialized');
    }

    // ========================================
    // PROGRESSIVE WEB APP FEATURES
    // ========================================
    
    async initializePWA() {
        console.log('📱 Initializing PWA features...');
        
        // Register service worker
        if ('serviceWorker' in navigator) {
            try {
                const registration = await navigator.serviceWorker.register('/static/sw.js');
                console.log('✅ Service Worker registered:', registration);
                
                // Handle updates
                registration.addEventListener('updatefound', () => {
                    this.handleServiceWorkerUpdate(registration);
                });
                
            } catch (error) {
                console.error('❌ Service Worker registration failed:', error);
            }
        }
        
        // Handle install prompt
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            this.installPrompt = e;
            this.showPWAInstallBanner();
        });
        
        // Handle app installed
        window.addEventListener('appinstalled', () => {
            console.log('✅ PWA installed successfully');
            this.hidePWAInstallBanner();
        });
        
        // Initialize PWA features
    // Removed automatic push permission request; will prompt on user gesture via requestNotifications()
        this.initializeBackgroundSync();
        this.initializeOfflineSupport();
    }
    
    showPWAInstallBanner() {
        const banner = document.createElement('div');
        banner.className = 'pwa-install-banner';
        banner.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h6 class="mb-1">📱 Install Research QA App</h6>
                    <small>Get the full experience with offline support and push notifications</small>
                </div>
                <div>
                    <button class="btn btn-light btn-sm me-2" onclick="phase3Manager.installPWA()">
                        Install
                    </button>
                    <button class="btn btn-outline-light btn-sm" onclick="this.parentElement.parentElement.parentElement.remove()">
                        ×
                    </button>
                </div>
            </div>
        `;
        
        document.body.insertBefore(banner, document.body.firstChild);
        setTimeout(() => banner.classList.add('show'), 100);
    }
    
    async installPWA() {
        if (this.installPrompt) {
            this.installPrompt.prompt();
            const result = await this.installPrompt.userChoice;
            console.log('PWA install result:', result);
            this.installPrompt = null;
        }
    }
    
    hidePWAInstallBanner() {
        const banner = document.querySelector('.pwa-install-banner');
        if (banner) banner.remove();
    }
    
    async requestNotifications() {
        if (!('Notification' in window)) return;
        if (Notification.permission === 'default') {
            try {
                const perm = await Notification.requestPermission();
                if (perm === 'granted') {
                    console.log('✅ Notifications enabled');
                } else {
                    console.log('Notification permission:', perm);
                }
            } catch(e){ console.warn('Notification request failed', e); }
        }
    }
    
    initializeBackgroundSync() {
        if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
            console.log('✅ Background sync available');
        }
    }
    
    initializeOfflineSupport() {
        // Handle online/offline events
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.updateConnectionStatus();
            this.syncOfflineActions();
        });
        
        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.updateConnectionStatus();
        });
        
        this.updateConnectionStatus();
    }

    // ========================================
    // D3.JS VISUALIZATIONS
    // ========================================
    
    initializeD3Visualizations() {
        console.log('📊 Initializing D3.js visualizations...');
        
        // Initialize different chart types
        this.initializePortfolioSunburst();
        this.initializeMarketTrendLine();
        this.initializeAnalystNetwork();
        this.initializeRealTimeStockChart();
        this.initializeRiskHeatmap();
    }
    
    initializePortfolioSunburst() {
        const container = document.getElementById('portfolio-sunburst');
        if (!container) return;
        
        const width = container.clientWidth;
        const height = 400;
        const radius = Math.min(width, height) / 2;
        
        // Sample data
        const data = {
            name: "Portfolio",
            children: [
                {
                    name: "Stocks",
                    children: [
                        { name: "Technology", value: 45000 },
                        { name: "Healthcare", value: 25000 },
                        { name: "Finance", value: 30000 }
                    ]
                },
                {
                    name: "Bonds",
                    children: [
                        { name: "Government", value: 15000 },
                        { name: "Corporate", value: 10000 }
                    ]
                },
                {
                    name: "Crypto",
                    children: [
                        { name: "Bitcoin", value: 8000 },
                        { name: "Ethereum", value: 5000 }
                    ]
                }
            ]
        };
        
        const svg = d3.select(container)
            .append('svg')
            .attr('width', width)
            .attr('height', height);
            
        const g = svg.append('g')
            .attr('transform', `translate(${width/2},${height/2})`);
            
        const partition = d3.partition().size([2 * Math.PI, radius]);
        const arc = d3.arc()
            .startAngle(d => d.x0)
            .endAngle(d => d.x1)
            .innerRadius(d => d.y0)
            .outerRadius(d => d.y1);
            
        const color = d3.scaleOrdinal(d3.schemeCategory10);
        
        const root = d3.hierarchy(data)
            .sum(d => d.value)
            .sort((a, b) => b.value - a.value);
            
        partition(root);
        
        g.selectAll('path')
            .data(root.descendants())
            .enter().append('path')
            .attr('d', arc)
            .style('fill', d => color(d.data.name))
            .style('stroke', '#fff')
            .style('stroke-width', 2)
            .on('mouseover', this.showTooltip.bind(this))
            .on('mouseout', this.hideTooltip.bind(this))
            .transition()
            .duration(1000)
            .attrTween('d', function(d) {
                const interpolate = d3.interpolate({x0: 0, x1: 0, y0: 0, y1: 0}, d);
                return function(t) {
                    return arc(interpolate(t));
                };
            });
            
        this.d3Charts.set('portfolio-sunburst', { svg, data, update: this.updatePortfolioSunburst.bind(this) });
    }
    
    initializeMarketTrendLine() {
        const container = document.getElementById('market-trend-chart');
        if (!container) return;
        
        const margin = { top: 20, right: 30, bottom: 40, left: 50 };
        const width = container.clientWidth - margin.left - margin.right;
        const height = 300 - margin.top - margin.bottom;
        
        // Generate sample time series data
        const data = d3.range(30).map(i => ({
            date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000),
            value: 100 + Math.random() * 50 + i * 2
        }));
        
        const svg = d3.select(container)
            .append('svg')
            .attr('width', width + margin.left + margin.right)
            .attr('height', height + margin.top + margin.bottom);
            
        const g = svg.append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);
            
        const x = d3.scaleTime()
            .domain(d3.extent(data, d => d.date))
            .range([0, width]);
            
        const y = d3.scaleLinear()
            .domain(d3.extent(data, d => d.value))
            .range([height, 0]);
            
        const line = d3.line()
            .x(d => x(d.date))
            .y(d => y(d.value))
            .curve(d3.curveMonotoneX);
            
        // Add gradient
        const gradient = svg.append('defs')
            .append('linearGradient')
            .attr('id', 'line-gradient')
            .attr('gradientUnits', 'userSpaceOnUse')
            .attr('x1', 0).attr('y1', height)
            .attr('x2', 0).attr('y2', 0);
            
        gradient.append('stop')
            .attr('offset', '0%')
            .attr('stop-color', '#0d6efd')
            .attr('stop-opacity', 0.1);
            
        gradient.append('stop')
            .attr('offset', '100%')
            .attr('stop-color', '#0d6efd')
            .attr('stop-opacity', 0.8);
            
        // Add axes
        g.append('g')
            .attr('transform', `translate(0,${height})`)
            .call(d3.axisBottom(x).tickFormat(d3.timeFormat('%m/%d')));
            
        g.append('g')
            .call(d3.axisLeft(y));
            
        // Add area
        const area = d3.area()
            .x(d => x(d.date))
            .y0(height)
            .y1(d => y(d.value))
            .curve(d3.curveMonotoneX);
            
        g.append('path')
            .datum(data)
            .attr('fill', 'url(#line-gradient)')
            .attr('d', area)
            .style('opacity', 0)
            .transition()
            .duration(1500)
            .style('opacity', 1);
            
        // Add line
        const path = g.append('path')
            .datum(data)
            .attr('fill', 'none')
            .attr('stroke', '#0d6efd')
            .attr('stroke-width', 3)
            .attr('d', line);
            
        // Animate line drawing
        const totalLength = path.node().getTotalLength();
        path
            .attr('stroke-dasharray', totalLength + ' ' + totalLength)
            .attr('stroke-dashoffset', totalLength)
            .transition()
            .duration(2000)
            .attr('stroke-dashoffset', 0);
            
        this.d3Charts.set('market-trend', { svg, data, x, y, line, update: this.updateMarketTrend.bind(this) });
    }
    
    initializeAnalystNetwork() {
        const container = document.getElementById('analyst-network');
        if (!container) return;
        
        const width = container.clientWidth;
        const height = 400;
        
        // Sample network data
        const nodes = [
            { id: 'center', group: 0, size: 30, name: 'Research QA' },
            { id: 'analyst1', group: 1, size: 20, name: 'Tech Analyst' },
            { id: 'analyst2', group: 1, size: 18, name: 'Finance Expert' },
            { id: 'analyst3', group: 1, size: 15, name: 'Market Specialist' },
            { id: 'investor1', group: 2, size: 12, name: 'Investor A' },
            { id: 'investor2', group: 2, size: 12, name: 'Investor B' },
            { id: 'investor3', group: 2, size: 12, name: 'Investor C' }
        ];
        
        const links = [
            { source: 'center', target: 'analyst1', value: 3 },
            { source: 'center', target: 'analyst2', value: 3 },
            { source: 'center', target: 'analyst3', value: 3 },
            { source: 'analyst1', target: 'investor1', value: 2 },
            { source: 'analyst1', target: 'investor2', value: 1 },
            { source: 'analyst2', target: 'investor2', value: 2 },
            { source: 'analyst2', target: 'investor3', value: 1 },
            { source: 'analyst3', target: 'investor1', value: 1 },
            { source: 'analyst3', target: 'investor3', value: 2 }
        ];
        
        const svg = d3.select(container)
            .append('svg')
            .attr('width', width)
            .attr('height', height);
            
        const simulation = d3.forceSimulation(nodes)
            .force('link', d3.forceLink(links).id(d => d.id).distance(80))
            .force('charge', d3.forceManyBody().strength(-200))
            .force('center', d3.forceCenter(width / 2, height / 2));
            
        const color = d3.scaleOrdinal(['#0d6efd', '#198754', '#fd7e14']);
        
        // Add links
        const link = svg.append('g')
            .selectAll('line')
            .data(links)
            .enter().append('line')
            .attr('stroke', '#999')
            .attr('stroke-opacity', 0.6)
            .attr('stroke-width', d => Math.sqrt(d.value) * 2);
            
        // Add nodes
        const node = svg.append('g')
            .selectAll('circle')
            .data(nodes)
            .enter().append('circle')
            .attr('r', d => d.size)
            .attr('fill', d => color(d.group))
            .attr('stroke', '#fff')
            .attr('stroke-width', 2)
            .call(this.drag(simulation));
            
        // Add labels
        const label = svg.append('g')
            .selectAll('text')
            .data(nodes)
            .enter().append('text')
            .text(d => d.name)
            .attr('font-size', 12)
            .attr('text-anchor', 'middle')
            .attr('dy', 4);
            
        simulation.on('tick', () => {
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);
                
            node
                .attr('cx', d => d.x)
                .attr('cy', d => d.y);
                
            label
                .attr('x', d => d.x)
                .attr('y', d => d.y);
        });
        
        this.d3Charts.set('analyst-network', { svg, simulation, nodes, links });
    }
    
    initializeRealTimeStockChart() {
        const container = document.getElementById('realtime-stock-chart');
        if (!container) return;
        
        const margin = { top: 20, right: 30, bottom: 40, left: 50 };
        const width = container.clientWidth - margin.left - margin.right;
        const height = 250 - margin.top - margin.bottom;
        
        let data = [];
        const maxDataPoints = 50;
        
        const svg = d3.select(container)
            .append('svg')
            .attr('width', width + margin.left + margin.right)
            .attr('height', height + margin.top + margin.bottom);
            
        const g = svg.append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);
            
        const x = d3.scaleTime().range([0, width]);
        const y = d3.scaleLinear().range([height, 0]);
        
        const line = d3.line()
            .x(d => x(d.time))
            .y(d => y(d.price))
            .curve(d3.curveMonotoneX);
            
        const xAxis = g.append('g')
            .attr('transform', `translate(0,${height})`);
            
        const yAxis = g.append('g');
        
        const path = g.append('path')
            .attr('fill', 'none')
            .attr('stroke', '#0d6efd')
            .attr('stroke-width', 2);
            
        // Simulate real-time data
        const updateData = () => {
            const now = new Date();
            const price = 100 + Math.random() * 20 + Math.sin(now.getTime() / 10000) * 10;
            
            data.push({ time: now, price: price });
            
            if (data.length > maxDataPoints) {
                data.shift();
            }
            
            x.domain(d3.extent(data, d => d.time));
            y.domain(d3.extent(data, d => d.price));
            
            xAxis.transition().duration(500).call(d3.axisBottom(x).tickFormat(d3.timeFormat('%H:%M:%S')));
            yAxis.transition().duration(500).call(d3.axisLeft(y));
            
            path.datum(data)
                .transition()
                .duration(500)
                .attr('d', line);
        };
        
        // Update every 2 seconds
        setInterval(updateData, 2000);
        
        this.d3Charts.set('realtime-stock', { updateData });
    }
    
    initializeRiskHeatmap() {
        const container = document.getElementById('risk-heatmap');
        if (!container) return;
        
        const width = container.clientWidth;
        const height = 300;
        const cellSize = 30;
        
        // Sample risk data
        const riskData = [
            { sector: 'Technology', metric: 'Volatility', value: 0.8 },
            { sector: 'Technology', metric: 'Correlation', value: 0.6 },
            { sector: 'Technology', metric: 'Liquidity', value: 0.9 },
            { sector: 'Healthcare', metric: 'Volatility', value: 0.5 },
            { sector: 'Healthcare', metric: 'Correlation', value: 0.4 },
            { sector: 'Healthcare', metric: 'Liquidity', value: 0.7 },
            { sector: 'Finance', metric: 'Volatility', value: 0.7 },
            { sector: 'Finance', metric: 'Correlation', value: 0.8 },
            { sector: 'Finance', metric: 'Liquidity', value: 0.8 }
        ];
        
        const sectors = [...new Set(riskData.map(d => d.sector))];
        const metrics = [...new Set(riskData.map(d => d.metric))];
        
        const svg = d3.select(container)
            .append('svg')
            .attr('width', width)
            .attr('height', height);
            
        const xScale = d3.scaleBand()
            .domain(metrics)
            .range([50, width - 50])
            .padding(0.1);
            
        const yScale = d3.scaleBand()
            .domain(sectors)
            .range([50, height - 50])
            .padding(0.1);
            
        const colorScale = d3.scaleSequential()
            .domain([0, 1])
            .interpolator(d3.interpolateYlOrRd);
            
        // Add cells
        svg.selectAll('rect')
            .data(riskData)
            .enter().append('rect')
            .attr('x', d => xScale(d.metric))
            .attr('y', d => yScale(d.sector))
            .attr('width', xScale.bandwidth())
            .attr('height', yScale.bandwidth())
            .attr('fill', d => colorScale(d.value))
            .attr('stroke', '#fff')
            .attr('stroke-width', 2)
            .style('opacity', 0)
            .transition()
            .duration(1000)
            .delay((d, i) => i * 100)
            .style('opacity', 1);
            
        // Add labels
        svg.selectAll('.x-label')
            .data(metrics)
            .enter().append('text')
            .attr('class', 'x-label')
            .attr('x', d => xScale(d) + xScale.bandwidth() / 2)
            .attr('y', 40)
            .attr('text-anchor', 'middle')
            .text(d => d);
            
        svg.selectAll('.y-label')
            .data(sectors)
            .enter().append('text')
            .attr('class', 'y-label')
            .attr('x', 40)
            .attr('y', d => yScale(d) + yScale.bandwidth() / 2)
            .attr('text-anchor', 'end')
            .attr('dominant-baseline', 'middle')
            .text(d => d);
            
        this.d3Charts.set('risk-heatmap', { svg, data: riskData });
    }

    // ========================================
    // REAL-TIME FEATURES
    // ========================================
    
    initializeRealtime() {
        console.log('⚡ Initializing real-time features...');
        
        // Initialize WebSocket connections
        this.initializeWebSocket();
        
        // Initialize real-time indicators
        this.initializeRealtimeIndicators();
        
        // Initialize automatic updates
        this.initializeAutoUpdates();
    }
    
    initializeWebSocket() {
        // Simulate WebSocket connection
        const wsUrl = `ws://${window.location.host}/ws`;
        console.log('🔌 Connecting to WebSocket:', wsUrl);
        
        // For demo purposes, simulate real-time updates
        this.simulateRealtimeUpdates();
    }
    
    simulateRealtimeUpdates() {
        // Simulate market data updates
        setInterval(() => {
            this.updateMarketData();
        }, 5000);
        
        // Simulate notification updates
        setInterval(() => {
            this.updateNotificationCount();
        }, 10000);
        
        // Simulate performance metrics
        setInterval(() => {
            this.updatePerformanceMetrics();
        }, 15000);
    }
    
    updateMarketData() {
        const elements = document.querySelectorAll('[data-realtime="market"]');
        elements.forEach(element => {
            const change = (Math.random() - 0.5) * 10;
            const isPositive = change > 0;
            
            element.classList.remove('text-success', 'text-danger');
            element.classList.add(isPositive ? 'text-success' : 'text-danger');
            
            element.innerHTML = `
                <i class="bi bi-arrow-${isPositive ? 'up' : 'down'}"></i>
                ${Math.abs(change).toFixed(2)}%
            `;
            
            // Add flash effect
            element.style.backgroundColor = isPositive ? '#d4edda' : '#f8d7da';
            setTimeout(() => {
                element.style.backgroundColor = 'transparent';
            }, 1000);
        });
    }
    
    updateNotificationCount() {
        const counter = document.querySelector('.realtime-counter');
        if (counter) {
            const currentCount = parseInt(counter.textContent) || 0;
            const newCount = currentCount + Math.floor(Math.random() * 3);
            counter.textContent = newCount;
            counter.style.animation = 'countUp 0.5s ease-out';
        }
    }
    
    updatePerformanceMetrics() {
        const metrics = document.querySelectorAll('[data-realtime="performance"]');
        metrics.forEach(metric => {
            const value = (Math.random() * 100).toFixed(1);
            metric.textContent = `${value}%`;
            
            // Update progress bars if present
            const progressBar = metric.parentElement.querySelector('.progress-bar');
            if (progressBar) {
                progressBar.style.width = `${value}%`;
            }
        });
    }
    
    initializeRealtimeIndicators() {
        // Add real-time indicators to relevant elements
        const indicators = document.querySelectorAll('[data-realtime]');
        indicators.forEach(indicator => {
            const dot = document.createElement('span');
            dot.className = 'realtime-dot ms-2';
            indicator.appendChild(dot);
        });
    }
    
    initializeAutoUpdates() {
        // Auto-refresh certain sections
        setInterval(() => {
            this.refreshDashboardData();
        }, 30000); // 30 seconds
    }
    
    async refreshDashboardData() {
        const elements = document.querySelectorAll('[data-auto-refresh]');
        elements.forEach(async (element) => {
            const url = element.dataset.autoRefresh;
            if (url) {
                try {
                    const response = await fetch(url);
                    const html = await response.text();
                    element.innerHTML = html;
                } catch (error) {
                    console.error('Auto-refresh failed:', error);
                }
            }
        });
    }

    // ========================================
    // MOBILE-FIRST RESPONSIVE FEATURES
    // ========================================
    
    initializeMobileFirst() {
        console.log('📱 Initializing mobile-first features...');
        
        this.initializeMobileNavigation();
        this.initializeTouchGestures();
        this.initializeResponsiveCharts();
        this.initializeMobileOptimizations();
    }
    
    initializeMobileNavigation() {
        // Add mobile header if on mobile
        if (window.innerWidth <= this.mobileBreakpoint) {
            this.addMobileHeader();
        }
        
        // Handle window resize
        window.addEventListener('resize', () => {
            if (window.innerWidth <= this.mobileBreakpoint) {
                this.addMobileHeader();
                this.enableMobileSidebar();
            } else {
                this.removeMobileHeader();
                this.disableMobileSidebar();
            }
        });
    }
    
    addMobileHeader() {
        if (document.querySelector('.mobile-header')) return;
        
        const header = document.createElement('div');
        header.className = 'mobile-header d-md-none';
        header.innerHTML = `
            <button class="mobile-menu-toggle" onclick="phase3Manager.toggleMobileSidebar()">
                <i class="bi bi-list"></i>
            </button>
            <h6 class="mb-0 flex-grow-1">Research QA Platform</h6>
            <div class="connection-status ${this.isOnline ? 'connected' : 'disconnected'}">
                <span class="status-dot ${this.isOnline ? 'connected' : 'disconnected'}"></span>
                ${this.isOnline ? 'Online' : 'Offline'}
            </div>
        `;
        
        document.body.insertBefore(header, document.body.firstChild);
    }
    
    removeMobileHeader() {
        const header = document.querySelector('.mobile-header');
        if (header) header.remove();
    }
    
    enableMobileSidebar() {
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            sidebar.classList.add('mobile-sidebar');
        }
    }
    
    disableMobileSidebar() {
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            sidebar.classList.remove('mobile-sidebar', 'show');
        }
        this.removeSidebarOverlay();
    }
    
    toggleMobileSidebar() {
        const sidebar = document.querySelector('.sidebar');
        if (!sidebar) return;
        
        sidebar.classList.toggle('show');
        
        if (sidebar.classList.contains('show')) {
            this.addSidebarOverlay();
        } else {
            this.removeSidebarOverlay();
        }
    }
    
    addSidebarOverlay() {
        if (document.querySelector('.sidebar-overlay')) return;
        
        const overlay = document.createElement('div');
        overlay.className = 'sidebar-overlay';
        overlay.onclick = () => this.toggleMobileSidebar();
        
        document.body.appendChild(overlay);
        setTimeout(() => overlay.classList.add('show'), 10);
    }
    
    removeSidebarOverlay() {
        const overlay = document.querySelector('.sidebar-overlay');
        if (overlay) {
            overlay.classList.remove('show');
            setTimeout(() => overlay.remove(), 300);
        }
    }
    
    initializeTouchGestures() {
        // Add touch gesture support for charts
        const charts = document.querySelectorAll('.d3-chart-container');
        charts.forEach(chart => {
            let startX, startY;
            
            chart.addEventListener('touchstart', (e) => {
                startX = e.touches[0].clientX;
                startY = e.touches[0].clientY;
            });
            
            chart.addEventListener('touchmove', (e) => {
                e.preventDefault(); // Prevent scrolling
            });
            
            chart.addEventListener('touchend', (e) => {
                const endX = e.changedTouches[0].clientX;
                const endY = e.changedTouches[0].clientY;
                
                const deltaX = endX - startX;
                const deltaY = endY - startY;
                
                // Handle swipe gestures
                if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {
                    if (deltaX > 0) {
                        this.handleSwipeRight(chart);
                    } else {
                        this.handleSwipeLeft(chart);
                    }
                }
            });
        });
    }
    
    handleSwipeLeft(chart) {
        // Navigate to next chart or data period
        console.log('Swipe left on chart:', chart);
    }
    
    handleSwipeRight(chart) {
        // Navigate to previous chart or data period
        console.log('Swipe right on chart:', chart);
    }
    
    initializeResponsiveCharts() {
        // Make D3 charts responsive
        const resizeCharts = () => {
            this.d3Charts.forEach((chart, key) => {
                if (chart.update) {
                    chart.update();
                }
            });
        };
        
        window.addEventListener('resize', this.debounce(resizeCharts, 250));
    }
    
    initializeMobileOptimizations() {
        // Optimize for mobile performance
        if (window.innerWidth <= this.mobileBreakpoint) {
            // Reduce animation complexity
            document.documentElement.style.setProperty('--animation-duration', '0.2s');
            
            // Enable hardware acceleration
            const cards = document.querySelectorAll('.card, .advanced-card');
            cards.forEach(card => {
                card.classList.add('gpu-accelerated');
            });
        }
    }

    // ========================================
    // CONNECTION MONITORING
    // ========================================
    
    initializeConnectionMonitoring() {
        console.log('🌐 Initializing connection monitoring...');
        
        // Create connection status indicator
        this.createConnectionStatusIndicator();
        
        // Monitor connection quality
        this.monitorConnectionQuality();
    }
    
    createConnectionStatusIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'connection-status-indicator';
        indicator.className = `connection-status ${this.isOnline ? 'connected' : 'disconnected'}`;
        indicator.innerHTML = `
            <span class="status-dot ${this.isOnline ? 'connected' : 'disconnected'}"></span>
        `;
        
        // The positioning is now handled in CSS
        indicator.style.cssText = `
            font-size: 0.875rem;
        `;
        
        document.body.appendChild(indicator);
    }
    
    updateConnectionStatus() {
        const indicator = document.getElementById('connection-status-indicator');
        const mobileStatus = document.querySelector('.mobile-header .connection-status');
        
        [indicator, mobileStatus].forEach(element => {
            if (element) {
                element.className = `connection-status ${this.isOnline ? 'connected' : 'disconnected'}`;
                element.innerHTML = `
                    <span class="status-dot ${this.isOnline ? 'connected' : 'disconnected'}"></span>
                `;
            }
        });
    }
    
    async monitorConnectionQuality() {
        if ('connection' in navigator) {
            const connection = navigator.connection;
            
            const updateConnectionInfo = () => {
                console.log('Connection type:', connection.effectiveType);
                console.log('Downlink speed:', connection.downlink);
                
                // Adjust features based on connection quality
                if (connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g') {
                    this.enableLowBandwidthMode();
                } else {
                    this.disableLowBandwidthMode();
                }
            };
            
            connection.addEventListener('change', updateConnectionInfo);
            updateConnectionInfo();
        }
    }
    
    enableLowBandwidthMode() {
        console.log('🐌 Low bandwidth mode enabled');
        // Reduce update frequency
        document.documentElement.style.setProperty('--animation-duration', '0.1s');
        
        // Disable auto-refresh
        clearInterval(this.autoRefreshInterval);
    }
    
    disableLowBandwidthMode() {
        console.log('🚄 Normal bandwidth mode');
        document.documentElement.style.setProperty('--animation-duration', '0.3s');
    }

    // ========================================
    // PERFORMANCE OPTIMIZATIONS
    // ========================================
    
    initializePerformanceOptimizations() {
        console.log('⚡ Initializing performance optimizations...');
        
        this.initializeLazyLoading();
        this.initializeVirtualScrolling();
        this.initializeImageOptimization();
        this.initializeMemoryManagement();
    }
    
    initializeLazyLoading() {
        // Lazy load charts and heavy components
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const element = entry.target;
                    
                    if (element.dataset.lazyChart) {
                        this.loadChart(element.dataset.lazyChart, element);
                        observer.unobserve(element);
                    }
                }
            });
        }, { threshold: 0.1 });
        
        document.querySelectorAll('[data-lazy-chart]').forEach(element => {
            observer.observe(element);
        });
    }
    
    loadChart(chartType, container) {
        // Add loading skeleton
        container.innerHTML = '<div class="loading-skeleton chart"></div>';
        
        // Simulate chart loading
        setTimeout(() => {
            container.innerHTML = '<div class="d3-chart-container" id="' + chartType + '"></div>';
            
            // Initialize the specific chart
            switch (chartType) {
                case 'portfolio-sunburst':
                    this.initializePortfolioSunburst();
                    break;
                case 'market-trend':
                    this.initializeMarketTrendLine();
                    break;
                // Add other chart types
            }
        }, 500);
    }
    
    initializeVirtualScrolling() {
        // Implement virtual scrolling for large lists
        const largeDataTables = document.querySelectorAll('[data-virtual-scroll]');
        largeDataTables.forEach(table => {
            this.setupVirtualScrolling(table);
        });
    }
    
    setupVirtualScrolling(container) {
        // Basic virtual scrolling implementation
        const itemHeight = 50;
        const visibleItems = Math.ceil(container.clientHeight / itemHeight);
        const totalItems = parseInt(container.dataset.totalItems) || 1000;
        
        console.log(`Virtual scrolling: ${visibleItems} visible of ${totalItems} total`);
    }
    
    initializeImageOptimization() {
        // Implement responsive images and WebP support
        const images = document.querySelectorAll('img[data-src]');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('loading');
                        imageObserver.unobserve(img);
                    }
                });
            });
            
            images.forEach(img => imageObserver.observe(img));
        }
    }
    
    initializeMemoryManagement() {
        // Clean up resources when components are removed
        const mutationObserver = new MutationObserver((mutations) => {
            mutations.forEach(mutation => {
                mutation.removedNodes.forEach(node => {
                    if (node.nodeType === 1) { // Element node
                        this.cleanupResources(node);
                    }
                });
            });
        });
        
        mutationObserver.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    cleanupResources(element) {
        // Clean up D3 charts
        const chartId = element.id;
        if (this.d3Charts.has(chartId)) {
            const chart = this.d3Charts.get(chartId);
            if (chart.svg) {
                chart.svg.remove();
            }
            this.d3Charts.delete(chartId);
            console.log('Cleaned up chart:', chartId);
        }
        
        // Clean up event listeners
        const elementsWithListeners = element.querySelectorAll('[data-cleanup]');
        elementsWithListeners.forEach(el => {
            // Remove event listeners if tracked
            console.log('Cleaning up listeners for:', el);
        });
    }

    // ========================================
    // UTILITY FUNCTIONS
    // ========================================
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
    
    showTooltip(event, d) {
        const tooltip = d3.select('body').append('div')
            .attr('class', 'd3-tooltip show')
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 10) + 'px')
            .html(`<strong>${d.data.name}</strong><br/>Value: ${d.value || 'N/A'}`);
    }
    
    hideTooltip() {
        d3.selectAll('.d3-tooltip').remove();
    }
    
    drag(simulation) {
        function dragstarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }
        
        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }
        
        function dragended(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }
        
        return d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended);
    }
    
    // Chart update methods
    updatePortfolioSunburst(newData) {
        // Update portfolio sunburst with new data
        console.log('Updating portfolio sunburst:', newData);
    }
    
    updateMarketTrend(newData) {
        // Update market trend chart with new data
        console.log('Updating market trend:', newData);
    }
    
    syncOfflineActions() {
        // Sync any actions that were queued while offline
        console.log('🔄 Syncing offline actions...');
    }
    
    handleServiceWorkerUpdate(registration) {
        console.log('🔄 Service Worker update available');
        
        // Show update notification
        const updateBanner = document.createElement('div');
        updateBanner.className = 'alert alert-info';
        updateBanner.innerHTML = `
            <strong>Update Available!</strong> 
            <button class="btn btn-sm btn-primary ms-2" onclick="window.location.reload()">
                Refresh
            </button>
        `;
        
        document.body.insertBefore(updateBanner, document.body.firstChild);
    }
}

// Initialize Phase 3 when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.phase3Manager = new Phase3Manager();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Phase3Manager;
}
