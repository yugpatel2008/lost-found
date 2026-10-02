// ─── Mobile Menu ────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
    const button = document.getElementById('mobile-menu-button');
    const menu = document.getElementById('mobile-menu');
    if (button && menu) {
        button.addEventListener('click', () => {
            menu.classList.toggle('hidden');
        });
    }
});

// ─── Post Page: Item Type Toggle ─────────────────────────────────────────────
function toggleItemType(type) {
    const hiddenInput = document.getElementById('selected-type');
    if (!hiddenInput) return; // Not on post page, skip

    hiddenInput.value = type;

    // Reset all buttons
    document.querySelectorAll('.type-btn').forEach(btn => {
        btn.classList.remove('bg-primary/10', 'ring-2', 'ring-primary', 'text-primary');
        btn.classList.add('bg-gray-100', 'text-gray-600');
    });

    // Highlight selected button
    const activeBtn = document.querySelector(`.type-btn.type-${type}`);
    if (activeBtn) {
        activeBtn.classList.remove('bg-gray-100', 'text-gray-600');
        activeBtn.classList.add('bg-primary/10', 'ring-2', 'ring-primary', 'text-primary');
    }
}

document.addEventListener('DOMContentLoaded', function () {
    // Wire up type buttons if they exist (post page only)
    const typeBtns = document.querySelectorAll('.type-btn');
    if (typeBtns.length > 0) {
        typeBtns.forEach(btn => {
            btn.addEventListener('click', function () {
                const type = btn.classList.contains('type-lost') ? 'lost' : 'found';
                toggleItemType(type);
                // Also check the underlying radio
                const radio = btn.querySelector('input[type="radio"]');
                if (radio) radio.checked = true;
            });
        });
        // Default: activate "lost"
        toggleItemType('lost');
    }
});

// ─── Home Page: Search ───────────────────────────────────────────────────────
function handleHomeSearch(event) {
    if (event.key === 'Enter') {
        const query = document.getElementById('home-search').value.trim();
        if (query) {
            window.location.href = '/browse/?q=' + encodeURIComponent(query);
        }
    }
}

// ─── Home Page: Load Recent Posts ────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
    const container = document.getElementById('recent-posts-container');
    if (!container) return;

    fetch('/api/recent-items/')
        .then(res => res.json())
        .then(data => {
            if (data.items && data.items.length > 0) {
                container.innerHTML = data.items.map(item => renderItemCard(item)).join('');
            } else {
                container.innerHTML = `
                    <div class="col-span-3 text-center py-12 text-gray-500">
                        <i class="fas fa-box-open text-4xl mb-3 block text-gray-300"></i>
                        No items posted yet. <a href="/post/" class="text-primary font-medium">Be the first!</a>
                    </div>`;
            }
        })
        .catch(() => {
            container.innerHTML = `
                <div class="col-span-3 text-center py-12 text-gray-400">
                    <i class="fas fa-exclamation-circle text-3xl mb-3 block"></i>
                    Could not load recent items.
                </div>`;
        });
});

function renderItemCard(item) {
    const typeColor = item.item_type === 'lost'
        ? 'bg-yellow-100 text-yellow-700'
        : 'bg-green-100 text-green-700';
    const imgHtml = item.file_url
        ? `<img src="${item.file_url}" alt="Item" class="object-cover h-40 w-full">`
        : `<div class="bg-gray-100 h-40 w-full flex items-center justify-center"><i class="fas fa-box text-3xl text-gray-300"></i></div>`;
    const tags = item.tags
        ? item.tags.split(',').map(t => `<span class="bg-gray-100 text-gray-600 py-1 px-2 rounded-full text-xs">${t.trim()}</span>`).join('')
        : '';
    return `
        <div class="bg-white border border-gray-100 rounded-xl shadow hover:shadow-md transition-all overflow-hidden">
            <div class="relative">
                ${imgHtml}
                <div class="absolute top-3 right-3 ${typeColor} py-1 px-2.5 rounded-full text-xs font-medium">${item.item_type.toUpperCase()}</div>
            </div>
            <div class="p-5">
                <h3 class="text-lg font-bold mb-1 leading-snug">${item.name}</h3>
                <p class="text-gray-500 text-sm mb-3 line-clamp-2 h-10 overflow-hidden">${item.description}</p>
                <div class="flex items-center text-sm text-gray-500 mb-3">
                    <i class="fas fa-map-marker-alt mr-1.5 text-primary"></i>
                    <span class="truncate">${item.location_found}</span>
                    <span class="mx-2">·</span>
                    <i class="fas fa-calendar-alt mr-1.5 text-primary"></i>
                    <span>${item.date_found || ''}</span>
                </div>
                <div class="flex flex-wrap gap-1 mb-4">${tags}</div>
                <a href="/item_details/${item.id}/" class="w-full block bg-gray-50 hover:bg-gray-100 text-primary py-2.5 rounded-lg font-medium transition text-center text-sm">
                    View Details
                </a>
            </div>
        </div>`;
}

// ─── "View All" button on home page ─────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
    const viewAllBtn = document.querySelector('#home-view .flex.justify-between button');
    if (viewAllBtn) {
        viewAllBtn.addEventListener('click', () => {
            window.location.href = '/browse/';
        });
    }
});
