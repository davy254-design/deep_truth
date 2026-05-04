// Sidebar toggle
document.addEventListener('DOMContentLoaded', function() {
    const sidebarCollapse = document.getElementById('sidebarCollapse');
    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('content');
    
    if (sidebarCollapse) {
        sidebarCollapse.addEventListener('click', function() {
            sidebar.classList.toggle('active');
            content.classList.toggle('active');
        });
    }
    
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// File upload preview
function previewVideo(input, previewId) {
    const file = input.files[0];
    const preview = document.getElementById(previewId);
    
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.innerHTML = `
                <video controls style="max-width: 100%; max-height: 300px; border-radius: 10px;">
                    <source src="${e.target.result}" type="${file.type}">
                    Your browser does not support video playback.
                </video>
                <p class="mt-2 text-muted">
                    <strong>File:</strong> ${file.name}<br>
                    <strong>Size:</strong> ${(file.size / (1024 * 1024)).toFixed(2)} MB<br>
                    <strong>Type:</strong> ${file.type}
                </p>
            `;
        };
        reader.readAsDataURL(file);
    }
}

// Drag and drop functionality
function setupDragDrop(dropZoneId, inputId) {
    const dropZone = document.getElementById(dropZoneId);
    const fileInput = document.getElementById(inputId);
    
    if (!dropZone || !fileInput) return;
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight(e) {
        dropZone.classList.add('border-primary', 'bg-primary-subtle');
    }
    
    function unhighlight(e) {
        dropZone.classList.remove('border-primary', 'bg-primary-subtle');
    }
    
    dropZone.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        fileInput.files = files;
        
        // Trigger change event
        const event = new Event('change', { bubbles: true });
        fileInput.dispatchEvent(event);
    }
    
    // Click to upload
    dropZone.addEventListener('click', function() {
        fileInput.click();
    });
}