// main.js - Fixed version for restaurant management system

// Handle login form submission
const loginForm = document.getElementById('login-form');
if (loginForm) {
    console.log('Login form found, attaching event listener');
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        console.log('Attempting login for user:', username);
        
        // Show the error div for debugging
        const errorElement = document.getElementById('login-error');
        if (errorElement) {
            errorElement.textContent = 'Đang thực hiện đăng nhập...';
            errorElement.classList.remove('d-none');
        }
        
        fetch('/api/v1/auth/login/json', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
            credentials: 'include'
        })
        .then(response => {
            console.log('Login response status:', response.status);
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.detail || 'Đăng nhập thất bại');
                });
            }
            return response.json();
        })
        .then(data => {
            console.log('Login successful');
            // Lưu token vào localStorage (optional)
            localStorage.setItem('auth_token', data.access_token);
            // Trực tiếp chuyển hướng đến dashboard
            window.location.href = '/dashboard';
        })
        .catch(error => {
            console.error('Login error:', error);
            if (errorElement) {
                errorElement.textContent = error.message || 'Đăng nhập thất bại';
                errorElement.classList.remove('d-none');
            }
        });
    });
} else {
    console.warn('Login form not found');
}

// Menu Management Functions
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the menu management page by looking for the menu management heading
    const menuManagementPage = document.querySelector('h1');
    if (menuManagementPage && menuManagementPage.textContent.includes('Menu Management')) {
        console.log('Menu Management page detected, initializing functions');
        
        // Ensure Bootstrap is loaded before initializing
        if (typeof bootstrap === 'undefined') {
            console.error('Bootstrap is not loaded. Modal functions will not work.');
            // Try to load Bootstrap dynamically if not already loaded
            const bootstrapScript = document.createElement('script');
            bootstrapScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.3/js/bootstrap.bundle.min.js';
            bootstrapScript.onload = function() {
                console.log('Bootstrap loaded dynamically, initializing menu functions');
                initializeMenuFunctions();
            };
            bootstrapScript.onerror = function() {
                console.error('Failed to load Bootstrap dynamically');
                alert('Could not load required scripts. Please refresh the page and try again.');
            };
            document.head.appendChild(bootstrapScript);
        } else {
            // Bootstrap is already loaded, proceed with initialization
            initializeMenuFunctions();
        }
    }
});

function initializeMenuFunctions() {
    console.log('Initializing menu functions - v1.0.2');
    try {
        // Setup modal for Add Menu Item button
        const addMenuItemButton = document.getElementById('addMenuItemButton');
        if(addMenuItemButton) {
            console.log('Add button found');
            addMenuItemButton.addEventListener('click', function() {
                console.log('Add button clicked');
                try {
                    const addModal = new bootstrap.Modal(document.getElementById('addMenuItemModal'));
                    addModal.show();
                } catch (error) {
                    console.error('Error showing add modal:', error);
                    alert('Could not open add form. Please try again.');
                }
            });
        } else {
            console.warn('Add button not found');
        }
        
        // Set up event listeners
        const filterButton = document.getElementById('filterButton');
        if(filterButton) {
            filterButton.addEventListener('click', filterByCategory);
        } else {
            console.warn('Filter button not found');
        }
        
        const addItemBtn = document.getElementById('addItemBtn');
        if(addItemBtn) {
            addItemBtn.addEventListener('click', addMenuItem);
        } else {
            console.warn('Add item button not found');
        }
        
        const updateItemBtn = document.getElementById('updateItemBtn');
        if(updateItemBtn) {
            updateItemBtn.addEventListener('click', updateMenuItem);
        } else {
            console.warn('Update item button not found');
        }
        
        const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
        if(confirmDeleteBtn) {
            confirmDeleteBtn.addEventListener('click', confirmDelete);
        } else {
            console.warn('Confirm delete button not found');
        }
        
        // Setup event listeners for edit buttons
        const editButtons = document.querySelectorAll('.edit-btn');
        console.log(`Found ${editButtons.length} edit buttons`);
        editButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                const itemId = this.dataset.id;
                console.log(`Edit button clicked for item ${itemId}`);
                editMenuItem(itemId);
            });
        });
        
        // Setup event listeners for toggle buttons
        const toggleButtons = document.querySelectorAll('.toggle-btn');
        console.log(`Found ${toggleButtons.length} toggle buttons`);
        toggleButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                const itemId = this.dataset.id;
                console.log(`Toggle button clicked for item ${itemId}`);
                toggleAvailability(itemId);
            });
        });
        
        // Setup event listeners for delete buttons
        const deleteButtons = document.querySelectorAll('.delete-btn');
        console.log(`Found ${deleteButtons.length} delete buttons`);
        deleteButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                const itemId = this.dataset.id;
                const itemName = this.closest('.card').querySelector('.card-title').textContent;
                console.log(`Delete button clicked for item ${itemId}: ${itemName}`);
                deleteMenuItem(itemId, itemName);
            });
        });
    } catch (error) {
        console.error('Error in menu initialization:', error);
    }
}

// Filter menu items by category
function filterByCategory() {
    console.log('Filtering by category');
    try {
        const categoryId = document.getElementById('categoryFilter').value;
        console.log(`Selected category: ${categoryId}`);
        const menuItems = document.querySelectorAll('.menu-item');
        
        let visibleCount = 0;
        menuItems.forEach(item => {
            if (categoryId === '0' || item.dataset.category === categoryId) {
                item.style.display = 'block';
                visibleCount++;
            } else {
                item.style.display = 'none';
            }
        });
        
        console.log(`Showing ${visibleCount} items after filtering`);
    } catch (error) {
        console.error('Error filtering by category:', error);
        alert('Error filtering menu items. Please try again.');
    }
}

// Add new menu item
async function addMenuItem() {
    console.log('Adding new menu item');
    try {
        const form = document.getElementById('addMenuItemForm');
        const formData = new FormData(form);
        const errorAlert = document.getElementById('addErrorAlert');
        
        // Basic validation
        if (!formData.get('name')) {
            errorAlert.textContent = 'Name is required';
            errorAlert.classList.remove('d-none');
            return;
        }
        
        if (!formData.get('price') || parseFloat(formData.get('price')) <= 0) {
            errorAlert.textContent = 'Price must be greater than 0';
            errorAlert.classList.remove('d-none');
            return;
        }
        
        errorAlert.classList.add('d-none');
        
        // Convert form data to JSON
        const jsonData = {
            name: formData.get('name'),
            description: formData.get('description') || "",
            price: parseFloat(formData.get('price')),
            category_id: parseInt(formData.get('category_id')),
            is_available: formData.get('is_available') === 'on'
        };
        
        console.log('Form data converted to JSON:', jsonData);
        
        // Get auth token from localStorage (if available)
        const token = localStorage.getItem('auth_token');
        const headers = {
            'Content-Type': 'application/json',
        };
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        // First create the menu item
        console.log('Sending POST request to create menu item');
        const response = await fetch('/api/v1/menu-items/', {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(jsonData),
            credentials: 'include'
        });
        
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            let errorDetail = 'Failed to create menu item';
            try {
                const errorData = await response.json();
                errorDetail = errorData.detail || errorDetail;
            } catch (e) {
                console.error('Error parsing error response:', e);
            }
            
            throw new Error(errorDetail);
        }
        
        const menuItem = await response.json();
        console.log('Menu item created:', menuItem);
        
        // If there's an image, upload it separately
        const imageFile = formData.get('image');
        if (imageFile && imageFile.size > 0) {
            console.log('Uploading image for new menu item');
            const imageFormData = new FormData();
            imageFormData.append('image', imageFile);
            
            // Add auth token to header if available
            const imageHeaders = {};
            if (token) {
                imageHeaders['Authorization'] = `Bearer ${token}`;
            }
            
            const uploadResponse = await fetch(`/api/v1/menu-items/${menuItem.menu_item_id}/upload-image`, {
                method: 'POST',
                headers: imageHeaders,
                body: imageFormData,
                credentials: 'include'
            });
            
            if (!uploadResponse.ok) {
                console.error('Failed to upload image');
                const errorData = await uploadResponse.json().catch(e => ({}));
                console.error('Upload error details:', errorData);
            } else {
                console.log('Image uploaded successfully');
            }
        }
        
        // Hide the modal
        const addModal = bootstrap.Modal.getInstance(document.getElementById('addMenuItemModal'));
        addModal.hide();
        
        // Show success message
        alert('Menu item added successfully!');
        
        // Refresh the page to show the new item
        window.location.reload();
        
    } catch (error) {
        console.error('Error adding menu item:', error);
        const errorAlert = document.getElementById('addErrorAlert');
        errorAlert.textContent = error.message;
        errorAlert.classList.remove('d-none');
    }
}

// Edit menu item
async function editMenuItem(itemId) {
    console.log(`Editing menu item ${itemId}`);
    try {
        const errorAlert = document.getElementById('editErrorAlert');
        errorAlert.classList.add('d-none');
        
        // Get token from localStorage if available
        const token = localStorage.getItem('auth_token');
        const headers = {};
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        console.log(`Fetching menu item ${itemId} details`);
        const response = await fetch(`/api/v1/menu-items/${itemId}`, {
            headers: headers,
            credentials: 'include'
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch menu item details');
        }
        
        const menuItem = await response.json();
        console.log('Menu item details:', menuItem);
        
        // Fill the edit form with the menu item details
        document.getElementById('editItemId').value = menuItem.menu_item_id;
        document.getElementById('editName').value = menuItem.name;
        document.getElementById('editDescription').value = menuItem.description || '';
        document.getElementById('editPrice').value = menuItem.price;
        document.getElementById('editCategory').value = menuItem.category_id;
        document.getElementById('editIsAvailable').checked = menuItem.is_available;
        
        // Show current image if available
        const imageContainer = document.getElementById('currentImageContainer');
        const currentImage = document.getElementById('currentImage');
        
        if (menuItem.image_url) {
            currentImage.src = menuItem.image_url;
            imageContainer.classList.remove('d-none');
        } else {
            imageContainer.classList.add('d-none');
        }
        
        // Open the edit modal
        const editModal = new bootstrap.Modal(document.getElementById('editMenuItemModal'));
        editModal.show();
        
    } catch (error) {
        console.error('Error fetching menu item details:', error);
        alert('Failed to load menu item details. Please try again.');
    }
}

// Update menu item
async function updateMenuItem() {
    console.log('Updating menu item');
    try {
        const form = document.getElementById('editMenuItemForm');
        const formData = new FormData(form);
        const itemId = formData.get('menu_item_id');
        const errorAlert = document.getElementById('editErrorAlert');
        
        // Basic validation
        if (!formData.get('name')) {
            errorAlert.textContent = 'Name is required';
            errorAlert.classList.remove('d-none');
            return;
        }
        
        if (!formData.get('price') || parseFloat(formData.get('price')) <= 0) {
            errorAlert.textContent = 'Price must be greater than 0';
            errorAlert.classList.remove('d-none');
            return;
        }
        
        errorAlert.classList.add('d-none');
        console.log(`Updating menu item ${itemId}`);
        
        // Convert form data to JSON
        const jsonData = {
            name: formData.get('name'),
            description: formData.get('description') || "",
            price: parseFloat(formData.get('price')),
            category_id: parseInt(formData.get('category_id')),
            is_available: formData.get('is_available') === 'on'
        };
        
        console.log('Form data converted to JSON:', jsonData);
        
        // Get token from localStorage if available
        const token = localStorage.getItem('auth_token');
        const headers = {
            'Content-Type': 'application/json',
        };
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        // Update the menu item
        console.log(`Sending PUT request to update menu item ${itemId}`);
        const response = await fetch(`/api/v1/menu-items/${itemId}`, {
            method: 'PUT',
            headers: headers,
            body: JSON.stringify(jsonData),
            credentials: 'include'
        });
        
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            let errorDetail = 'Failed to update menu item';
            try {
                const errorData = await response.json();
                errorDetail = errorData.detail || errorDetail;
            } catch (e) {
                console.error('Error parsing error response:', e);
            }
            
            throw new Error(errorDetail);
        }
        
        console.log('Menu item updated successfully');
        
        // If there's a new image, upload it separately
        const imageFile = formData.get('image');
        if (imageFile && imageFile.size > 0) {
            console.log(`Uploading new image for menu item ${itemId}`);
            const imageFormData = new FormData();
            imageFormData.append('image', imageFile);
            
            const imageHeaders = {};
            if (token) {
                imageHeaders['Authorization'] = `Bearer ${token}`;
            }
            
            const uploadResponse = await fetch(`/api/v1/menu-items/${itemId}/upload-image`, {
                method: 'POST',
                headers: imageHeaders,
                body: imageFormData,
                credentials: 'include'
            });
            
            if (!uploadResponse.ok) {
                console.error('Failed to upload image');
                const errorData = await uploadResponse.json().catch(e => ({}));
                console.error('Upload error details:', errorData);
            } else {
                console.log('Image uploaded successfully');
            }
        }
        
        // Hide the modal
        const editModal = bootstrap.Modal.getInstance(document.getElementById('editMenuItemModal'));
        editModal.hide();
        
        // Show success message
        alert('Menu item updated successfully!');
        
        // Refresh the page to show the updated item
        window.location.reload();
        
    } catch (error) {
        console.error('Error updating menu item:', error);
        const errorAlert = document.getElementById('editErrorAlert');
        errorAlert.textContent = error.message;
        errorAlert.classList.remove('d-none');
    }
}

// Toggle availability
async function toggleAvailability(itemId) {
    console.log(`Toggling availability for menu item ${itemId}`);
    try {
        // Get token from localStorage if available
        const token = localStorage.getItem('auth_token');
        const headers = {};
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        console.log(`Sending PUT request to toggle menu item ${itemId}`);
        const response = await fetch(`/api/v1/menu-items/${itemId}/toggle-availability`, {
            method: 'PUT',
            headers: headers,
            credentials: 'include'
        });
        
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            throw new Error('Failed to toggle availability');
        }
        
        console.log('Item availability toggled successfully');
        
        // Show success message
        alert('Item availability updated successfully!');
        
        // Refresh the page to show the updated status
        window.location.reload();
        
    } catch (error) {
        console.error('Error toggling availability:', error);
        alert('Failed to update item availability. Please try again.');
    }
}