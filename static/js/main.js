document.addEventListener('DOMContentLoaded', () => {
    // ----------------------------------------------------
    // Toast Alert Notification System
    // ----------------------------------------------------
    const createToastContainer = () => {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        return container;
    };

    window.showToast = (message, type = 'info') => {
        const container = createToastContainer();
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        let icon = 'info-circle';
        if (type === 'success') icon = 'check-circle';
        if (type === 'error') icon = 'exclamation-circle';
        if (type === 'warning') icon = 'exclamation-triangle';
        if (message.includes('PRICE DROP')) icon = 'bell';

        toast.innerHTML = `
            <i class="fas fa-${icon}"></i>
            <span>${message}</span>
        `;
        
        container.appendChild(toast);

        // Auto remove toast
        setTimeout(() => {
            toast.style.animation = 'toastSlideIn 0.3s ease reverse forwards';
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, 5000);
    };

    // ----------------------------------------------------
    // Local Compare Manager (Sticky bar and selection)
    // ----------------------------------------------------
    let compareList = [];

    // Load existing compare selection
    const compareCheckboxes = document.querySelectorAll('.compare-checkbox');
    const stickyBar = document.querySelector('.compare-sticky-bar');
    const compareCountSpan = document.getElementById('compare-count');
    const btnCompareNow = document.getElementById('btn-compare-now');

    const updateStickyBar = () => {
        if (!stickyBar) return;
        
        if (compareList.length > 0) {
            compareCountSpan.textContent = `${compareList.length}/3`;
            stickyBar.classList.add('active');
            
            if (compareList.length >= 2) {
                btnCompareNow.removeAttribute('disabled');
            } else {
                btnCompareNow.setAttribute('disabled', 'true');
            }
        } else {
            stickyBar.classList.remove('active');
        }
    };

    const handleCompareChange = (e) => {
        const productId = parseInt(e.target.dataset.id);
        const name = e.target.dataset.name;

        if (e.target.checked) {
            if (compareList.length >= 3) {
                e.target.checked = false;
                showToast("You can compare up to 3 products at a time.", "warning");
                return;
            }
            if (!compareList.includes(productId)) {
                compareList.push(productId);
                showToast(`Added ${name} to comparison list.`);
            }
        } else {
            compareList = compareList.filter(id => id !== productId);
            showToast(`Removed ${name} from comparison list.`);
        }
        updateStickyBar();
    };

    // Attach listeners to static compare checkboxes
    compareCheckboxes.forEach(cb => {
        cb.addEventListener('change', handleCompareChange);
    });

    if (btnCompareNow) {
        btnCompareNow.addEventListener('click', () => {
            if (compareList.length >= 2) {
                window.location.href = `/compare?ids=${compareList.join(',')}`;
            }
        });
    }

    // ----------------------------------------------------
    // Wishlist API Management
    // ----------------------------------------------------
    const attachWishlistListeners = () => {
        const heartButtons = document.querySelectorAll('.wishlist-heart-btn');
        heartButtons.forEach(btn => {
            // Remove previous event listener clone trick to avoid double binding
            const newBtn = btn.cloneNode(true);
            btn.parentNode.replaceChild(newBtn, btn);

            newBtn.addEventListener('click', async (e) => {
                e.stopPropagation();
                e.preventDefault();
                const productId = newBtn.dataset.id;
                
                try {
                    const response = await fetch('/api/wishlist/toggle', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ product_id: productId })
                    });
                    
                    if (response.status === 401) {
                        showToast("Please register or log in to add items to your wishlist.", "warning");
                        setTimeout(() => {
                            window.location.href = '/login';
                        }, 2000);
                        return;
                    }

                    const resData = await response.json();
                    if (resData.status === 'success') {
                        if (resData.action === 'added') {
                            newBtn.classList.add('active');
                            newBtn.querySelector('i').className = 'fas fa-heart';
                            showToast("Item added to wishlist!", "success");
                        } else {
                            newBtn.classList.remove('active');
                            newBtn.querySelector('i').className = 'far fa-heart';
                            showToast("Item removed from wishlist.");
                            
                            // If we are on the wishlist page, remove the card from the UI
                            const card = newBtn.closest('.product-card');
                            if (card && window.location.pathname === '/wishlist') {
                                card.style.animation = 'slideIn 0.3s ease reverse forwards';
                                setTimeout(() => card.remove(), 300);
                            }
                        }
                    }
                } catch (error) {
                    showToast("Error updating wishlist. Please try again.", "error");
                }
            });
        });
    };

    // Initialize wishlist binds
    attachWishlistListeners();

    // ----------------------------------------------------
    // Wishlist Target Price & simulated drop alert
    // ----------------------------------------------------
    const targetPriceInputs = document.querySelectorAll('.target-price-input');
    targetPriceInputs.forEach(input => {
        input.addEventListener('change', async (e) => {
            const productId = e.target.dataset.id;
            const targetVal = e.target.value;

            try {
                const response = await fetch('/api/wishlist/target_price', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ product_id: productId, target_price: targetVal })
                });
                const data = await response.json();
                if (data.status === 'success') {
                    showToast("Target price saved successfully!", "success");
                } else {
                    showToast(data.message || "Error saving target price.", "error");
                }
            } catch (err) {
                showToast("Connection failed.", "error");
            }
        });
    });

    const btnSimulate = document.getElementById('btn-simulate-alerts');
    if (btnSimulate) {
        btnSimulate.addEventListener('click', async () => {
            btnSimulate.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Checking Discounts...';
            btnSimulate.setAttribute('disabled', 'true');
            
            try {
                const response = await fetch('/api/wishlist/simulate_price_drop', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                const data = await response.json();
                btnSimulate.innerHTML = '<i class="fas fa-magic"></i> Simulate Price Drops';
                btnSimulate.removeAttribute('disabled');

                if (data.status === 'success') {
                    if (data.alerts.length === 0) {
                        showToast("Scanned wishlist items. No price drops matched target constraints this turn.", "info");
                    } else {
                        data.alerts.forEach(alert => {
                            showToast(alert.message, "success");
                            
                            // Highlight the item in UI with a green glow border
                            const itemCard = document.getElementById(`wish-card-${alert.product_id}`);
                            if (itemCard) {
                                itemCard.style.borderColor = 'var(--secondary)';
                                itemCard.style.boxShadow = '0 0 20px rgba(0, 242, 254, 0.4)';
                                
                                // Update displayed price temporarily to simulate sale
                                const priceTag = itemCard.querySelector('.product-price');
                                if (priceTag) {
                                    priceTag.innerHTML = `<span style="text-decoration: line-through; color: var(--text-muted); font-size: 0.95rem;">₹${alert.old_price.toLocaleString()}</span> <span style="color: var(--secondary);">₹${alert.new_price.toLocaleString()}</span>`;
                                }
                            }
                        });
                    }
                }
            } catch (err) {
                btnSimulate.innerHTML = '<i class="fas fa-magic"></i> Simulate Price Drops';
                btnSimulate.removeAttribute('disabled');
                showToast("Failed to simulate discount scanner.", "error");
            }
        });
    }

    // ----------------------------------------------------
    // AI Chat Engine UI Handler
    // ----------------------------------------------------
    const chatFeed = document.getElementById('chat-feed');
    const chatInput = document.getElementById('chat-input');
    const btnSend = document.getElementById('btn-send');
    const queryChips = document.querySelectorAll('.prompt-chips .chip');

    // Elasticity state
    const elasticityBtns = document.querySelectorAll('.elasticity-btn');
    let currentElasticity = 'strict';

    elasticityBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            elasticityBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentElasticity = btn.dataset.mode;
            showToast(`Budget elasticity updated to: ${currentElasticity.toUpperCase()}`, "info");
        });
    });

    const createTypingIndicator = () => {
        const div = document.createElement('div');
        div.className = 'typing-indicator';
        div.id = 'typing-indicator';
        div.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;
        return div;
    };

    const formatCurrency = (val) => {
        return '₹' + parseFloat(val).toLocaleString('en-IN', { maximumFractionDigits: 2 });
    };

    const submitChatMessage = async (text) => {
        if (!text.trim()) return;

        // 1. Render user query bubble
        const userBubble = document.createElement('div');
        userBubble.className = 'chat-bubble user';
        userBubble.textContent = text;
        chatFeed.appendChild(userBubble);
        
        chatFeed.scrollTop = chatFeed.scrollHeight;
        chatInput.value = '';

        // 2. Add loading spinner
        const loader = createTypingIndicator();
        chatFeed.appendChild(loader);
        chatFeed.scrollTop = chatFeed.scrollHeight;

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: text,
                    elasticity_mode: currentElasticity
                })
            });

            const data = await response.json();
            loader.remove();

            if (data.status === 'success') {
                const aiBubble = document.createElement('div');
                aiBubble.className = 'chat-bubble ai';

                // Build header chips representing parsed items
                let parsedHTML = '<div class="ai-meta">';
                if (data.parsed_query.category) {
                    parsedHTML += `<span class="badge badge-cat"><i class="fas fa-tag"></i> ${data.parsed_query.category}</span>`;
                }
                if (data.parsed_query.budget) {
                    parsedHTML += `<span class="badge badge-budget"><i class="fas fa-wallet"></i> ${formatCurrency(data.parsed_query.budget)} (${currentElasticity.toUpperCase()})</span>`;
                }
                if (data.parsed_query.keywords && data.parsed_query.keywords.length > 0) {
                    parsedHTML += `<span class="badge badge-keywords"><i class="fas fa-bullseye"></i> ${data.parsed_query.keywords.join(', ')}</span>`;
                }
                parsedHTML += '</div>';

                // Core response text
                let introText = '';
                if (data.recommendations.length === 0) {
                    introText = `<div class="ai-text">I searched our product database for items matching your query, but could not find options in that range. Try selecting **Flexible** budget mode or broadening your query category!</div>`;
                } else {
                    introText = `<div class="ai-text">Here are the best matching products I curated from our inventory based on your needs:</div>`;
                }

                aiBubble.innerHTML = parsedHTML + introText;

                // Build products grid if items found
                if (data.recommendations.length > 0) {
                    const grid = document.createElement('div');
                    grid.className = 'product-card-grid';

                    data.recommendations.forEach(item => {
                        const card = document.createElement('div');
                        card.className = 'product-card';
                        
                        card.innerHTML = `
                            <div class="card-img-wrapper">
                                <img src="${item.image_url}" alt="${item.name}">
                                <div class="wishlist-heart-btn ${item.is_wishlisted ? 'active' : ''}" data-id="${item.id}">
                                    <i class="${item.is_wishlisted ? 'fas' : 'far'} fa-heart"></i>
                                </div>
                            </div>
                            <div class="card-body">
                                <div class="card-meta-row">
                                    <span class="product-cat-tag">${item.category}</span>
                                    <span class="rating-badge"><i class="fas fa-star"></i> ${item.rating}</span>
                                </div>
                                <h3 class="product-title" title="${item.name}">${item.name}</h3>
                                <p class="product-desc">${item.description}</p>
                                <div class="product-price">${formatCurrency(item.price)}</div>
                                
                                <div class="ai-card-reason">
                                    <i class="fas fa-info-circle"></i>
                                    <span>${item.explanation}</span>
                                </div>
                                
                                <div class="card-actions">
                                    <a href="/product/${item.id}" class="btn-card primary">View Details</a>
                                    <label class="compare-checkbox-label">
                                        <input type="checkbox" class="compare-checkbox" data-id="${item.id}" data-name="${item.name}">
                                        <span>Add to Compare</span>
                                    </label>
                                </div>
                            </div>
                        `;
                        grid.appendChild(card);
                    });
                    aiBubble.appendChild(grid);
                }

                chatFeed.appendChild(aiBubble);
                
                // Re-bind listeners on dynamically loaded compare/wishlist nodes
                aiBubble.querySelectorAll('.compare-checkbox').forEach(cb => {
                    cb.addEventListener('change', handleCompareChange);
                });
                attachWishlistListeners();

            } else {
                const aiBubble = document.createElement('div');
                aiBubble.className = 'chat-bubble ai';
                aiBubble.innerHTML = `<div class="ai-text" style="color: var(--danger);">Sorry, I encountered an issue querying recommendations: ${data.message}</div>`;
                chatFeed.appendChild(aiBubble);
            }
            
            chatFeed.scrollTop = chatFeed.scrollHeight;

        } catch (err) {
            loader.remove();
            const aiBubble = document.createElement('div');
            aiBubble.className = 'chat-bubble ai';
            aiBubble.innerHTML = `<div class="ai-text" style="color: var(--danger);">Network error. Could not connect to AI Engine.</div>`;
            chatFeed.appendChild(aiBubble);
            chatFeed.scrollTop = chatFeed.scrollHeight;
        }
    };

    if (btnSend && chatInput) {
        btnSend.addEventListener('click', () => {
            submitChatMessage(chatInput.value);
        });

        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                submitChatMessage(chatInput.value);
            }
        });
    }

    queryChips.forEach(chip => {
        chip.addEventListener('click', () => {
            submitChatMessage(chip.textContent.trim());
        });
    });

    // Check if query parameter exists in URL and auto-run
    const urlParams = new URLSearchParams(window.location.search);
    const queryParam = urlParams.get('query');
    if (queryParam && chatInput) {
        // Clean URL parameter to prevent re-triggering on manual refresh
        const newUrl = window.location.protocol + "//" + window.location.host + window.location.pathname;
        window.history.pushState({ path: newUrl }, '', newUrl);
        
        setTimeout(() => {
            submitChatMessage(queryParam);
        }, 500);
    }

    // ----------------------------------------------------
    // Admin Dashboard tabs
    // ----------------------------------------------------
    const adminTabs = document.querySelectorAll('.admin-tab');
    const tabContents = document.querySelectorAll('.admin-tab-content');

    if (adminTabs.length > 0) {
        adminTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                adminTabs.forEach(t => t.classList.remove('active'));
                tabContents.forEach(c => c.classList.remove('active'));

                tab.classList.add('active');
                const targetId = tab.dataset.target;
                document.getElementById(targetId).classList.add('active');
            });
        });
    }

    // ----------------------------------------------------
    // Dynamic spec field generator in Admin Form
    // ----------------------------------------------------
    const specContainer = document.getElementById('spec-fields-container');
    const btnAddSpec = document.getElementById('btn-add-spec');
    let specIndex = 0;

    // Detect existing spec items count if modifying
    if (specContainer) {
        specIndex = specContainer.querySelectorAll('.spec-input-row').length;
    }

    if (btnAddSpec && specContainer) {
        btnAddSpec.addEventListener('click', () => {
            const row = document.createElement('div');
            row.className = 'spec-input-row';
            row.id = `spec-row-${specIndex}`;
            row.innerHTML = `
                <input type="text" name="spec_key_${specIndex}" placeholder="Specification Name (e.g. RAM)" required>
                <input type="text" name="spec_val_${specIndex}" placeholder="Value (e.g. 16GB)" required>
                <button type="button" class="btn-remove-spec" data-index="${specIndex}">
                    <i class="fas fa-trash"></i>
                </button>
            `;
            specContainer.appendChild(row);

            // Bind trash delete button
            row.querySelector('.btn-remove-spec').addEventListener('click', (e) => {
                const idx = e.currentTarget.dataset.index;
                document.getElementById(`spec-row-${idx}`).remove();
            });

            specIndex++;
        });

        // Bind existing trash buttons (in Edit mode)
        document.querySelectorAll('.btn-remove-spec').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const idx = e.currentTarget.dataset.index;
                const row = document.getElementById(`spec-row-${idx}`);
                if (row) row.remove();
            });
        });
    }
});
