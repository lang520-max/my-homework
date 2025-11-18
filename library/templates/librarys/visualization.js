// visualization.js
document.addEventListener('DOMContentLoaded', function() {
    console.log('图书馆管理系统已加载');

    // 1. 数字计数动画
    function animateNumbers() {
        const numberElements = document.querySelectorAll('.stat-number');
        numberElements.forEach(element => {
            const finalValue = parseInt(element.textContent) || 0;
            let current = 0;
            const increment = finalValue / 50;
            const duration = 2000;

            const timer = setInterval(() => {
                current += increment;
                if (current >= finalValue) {
                    element.textContent = finalValue.toLocaleString();
                    clearInterval(timer);
                } else {
                    element.textContent = Math.floor(current).toLocaleString();
                }
            }, duration / 50);
        });
    }

    // 延迟执行数字动画
    setTimeout(animateNumbers, 500);

    // 2. 卡片悬停效果
    const cards = document.querySelectorAll('.stat-card, .content-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 5px 15px rgba(0,0,0,0.2)';
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
        });
    });

    // 3. 列表项点击效果
    const listItems = document.querySelectorAll('.list-item');
    listItems.forEach(item => {
        item.addEventListener('click', function() {
            this.style.background = '#f0f8ff';
            setTimeout(() => {
                this.style.background = '';
            }, 300);
        });
    });

    // 4. 登录注册按钮功能
    function setupAuthButtons() {
        const loginBtn = document.querySelector('.btn-outline');
        const registerBtn = document.querySelector('.btn-primary');

        if (loginBtn) {
            loginBtn.addEventListener('click', function(e) {
                e.preventDefault();
                alert('登录功能开发中...');
            });
        }

        if (registerBtn) {
            registerBtn.addEventListener('click', function(e) {
                e.preventDefault();
                alert('注册功能开发中...');
            });
        }
    }

    // 5. 搜索功能（简化版）
    function setupSearch() {
        // 创建搜索框
        const searchHTML = `
            <div class="search-container" style="margin-top: 1rem;">
                <input type="text" id="globalSearch" placeholder="搜索图书、作者..."
                       style="padding: 0.5rem; width: 100%; max-width: 300px;
                              border: 1px solid #ddd; border-radius: 4px;">
            </div>
        `;

        const welcomeSection = document.querySelector('.welcome-section');
        welcomeSection.insertAdjacentHTML('beforeend', searchHTML);

        const searchInput = document.getElementById('globalSearch');
        if (searchInput) {
            searchInput.addEventListener('input', function(e) {
                const searchTerm = e.target.value.toLowerCase().trim();
                highlightSearchResults(searchTerm);
            });
        }
    }

    function highlightSearchResults(term) {
        const listItems = document.querySelectorAll('.list-item');

        listItems.forEach(item => {
            const text = item.textContent.toLowerCase();
            if (term === '' || text.includes(term)) {
                item.style.display = 'block';
                if (term) {
                    item.style.background = '#fff9e6';
                } else {
                    item.style.background = '';
                }
            } else {
                item.style.display = 'none';
            }
        });
    }

    // 6. 自动刷新数据（可选功能）
    function setupAutoRefresh() {
        // 每5分钟刷新一次页面
        setInterval(() => {
            if (confirm('数据已更新，是否刷新页面？')) {
                window.location.reload();
            }
        }, 300000); // 5分钟
    }

    // 7. 快速操作按钮效果
    function setupActionButtons() {
        const actionButtons = document.querySelectorAll('.action-btn');
        actionButtons.forEach(button => {
            button.addEventListener('mouseenter', function() {
                this.style.transform = 'scale(1.05)';
            });

            button.addEventListener('mouseleave', function() {
                this.style.transform = 'scale(1)';
            });
        });
    }

    // 初始化所有功能
    setupAuthButtons();
    setupSearch();
    setupActionButtons();
    // setupAutoRefresh(); // 可选：取消注释启用自动刷新

    console.log('所有功能初始化完成');
});