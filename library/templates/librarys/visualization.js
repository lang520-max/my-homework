// visualization.js
document.addEventListener('DOMContentLoaded', function() {
    console.log('智慧图书馆管理系统已加载');

    // 1. 统计卡片点击效果
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach(card => {
        card.addEventListener('click', function() {
            // 添加点击动画
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);

            // 显示统计信息（这里可以添加更多功能）
            const number = this.querySelector('.stat-number').textContent;
            const label = this.querySelector('.stat-label').textContent;
            console.log(`${label}: ${number}`);
        });
    });

    // 2. 数字计数动画
    function animateNumbers() {
        const numberElements = document.querySelectorAll('.stat-number');
        numberElements.forEach(element => {
            const target = parseInt(element.textContent) || 0;
            let current = 0;
            const increment = target / 50; // 控制动画速度
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                element.textContent = Math.floor(current).toLocaleString();
            }, 30);
        });
    }

    // 页面加载后执行数字动画
    setTimeout(animateNumbers, 500);

    // 3. 滚动动画效果
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // 为所有卡片添加观察
    const cards = document.querySelectorAll('.section-card, .stat-card');
    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });

    // 4. 实时时钟
    function updateClock() {
        const now = new Date();
        const timeString = now.toLocaleString('zh-CN', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            weekday: 'long',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });

        // 在页脚显示时间
        const footer = document.querySelector('footer p');
        if (footer) {
            const originalText = footer.innerHTML;
            footer.innerHTML = `📅 ${timeString} | ${originalText}`;
        }
    }

    // 每秒更新时钟
    setInterval(updateClock, 1000);
    updateClock(); // 立即执行一次

    // 5. 搜索功能（简单演示）
    function setupSearch() {
        // 创建搜索框
        const header = document.querySelector('header');
        const searchHTML = `
            <div style="margin-top: 20px;">
                <input type="text" id="bookSearch" placeholder="🔍 搜索图书..."
                       style="padding: 10px; width: 300px; max-width: 100%;
                              border: none; border-radius: 25px; text-align: center;">
            </div>
        `;
        header.insertAdjacentHTML('beforeend', searchHTML);

        const searchInput = document.getElementById('bookSearch');
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const bookItems = document.querySelectorAll('.book-item');

            bookItems.forEach(item => {
                const title = item.querySelector('.book-title').textContent.toLowerCase();
                if (title.includes(searchTerm)) {
                    item.style.display = 'block';
                    item.style.animation = 'fadeIn 0.3s ease';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }

    // 初始化搜索功能
    setupSearch();

    // 6. 主题切换功能
    function setupThemeToggle() {
        const themeButton = document.createElement('button');
        themeButton.innerHTML = '🌙 切换主题';
        themeButton.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 15px;
            background: rgba(255,255,255,0.2);
            border: none;
            border-radius: 20px;
            color: white;
            cursor: pointer;
            backdrop-filter: blur(10px);
            z-index: 1000;
        `;

        document.body.appendChild(themeButton);

        themeButton.addEventListener('click', function() {
            document.body.classList.toggle('dark-theme');
            this.innerHTML = document.body.classList.contains('dark-theme') ? '☀️ 亮色主题' : '🌙 暗色主题';
        });
    }

    // 暗色主题CSS
    const darkThemeCSS = `
        body.dark-theme {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: #ecf0f1;
        }

        body.dark-theme .stat-card,
        body.dark-theme .section-card {
            background: #34495e;
            color: #ecf0f1;
        }

        body.dark-theme .book-item,
        body.dark-theme .borrow-item {
            background: #2c3e50;
            color: #bdc3c7;
        }
    `;

    // 添加暗色主题样式
    const style = document.createElement('style');
    style.textContent = darkThemeCSS;
    document.head.appendChild(style);

    // 初始化主题切换
    setupThemeToggle();

    // 7. 数据刷新模拟
    function simulateDataRefresh() {
        setInterval(() => {
            const numbers = document.querySelectorAll('.stat-number');
            numbers.forEach(numberEl => {
                const current = parseInt(numberEl.textContent.replace(/,/g, '')) || 0;
                const newValue = current + Math.floor(Math.random() * 10);
                numberEl.textContent = newValue.toLocaleString();
            });
        }, 10000); // 每10秒刷新一次
    }

    // 开始模拟数据刷新
    simulateDataRefresh();
});