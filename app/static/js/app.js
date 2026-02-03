// File Upload with Drag & Drop
document.addEventListener('DOMContentLoaded', function() {
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('file-input');
    const uploadForm = document.getElementById('upload-form');
    const uploadProgress = document.getElementById('upload-progress');
    const uploadResult = document.getElementById('upload-result');

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Highlight drop area when dragging over
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });

    function highlight() {
        dropArea.classList.add('drag-over');
    }

    function unhighlight() {
        dropArea.classList.remove('drag-over');
    }

    // Handle dropped files
    dropArea.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;

        if (files.length > 0) {
            fileInput.files = files;
            uploadFile(files[0]);
        }
    }

    // Handle file input change
    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            uploadFile(this.files[0]);
        }
    });

    // Click on drop area to trigger file input
    dropArea.addEventListener('click', function() {
        fileInput.click();
    });

    async function uploadFile(file) {
        // Validate file type
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf'];
        if (!allowedTypes.includes(file.type)) {
            showError('Invalid file type. Please upload a JPG, PNG, or PDF file.');
            return;
        }

        // Validate file size (5MB)
        const maxSize = 5 * 1024 * 1024;
        if (file.size > maxSize) {
            showError('File too large. Maximum size is 5MB.');
            return;
        }

        // Show progress
        uploadForm.classList.add('hidden');
        uploadResult.classList.add('hidden');
        uploadProgress.classList.remove('hidden');

        // Upload file
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                showSuccess(result);
                // Trigger search refresh to show new receipt
                setTimeout(() => {
                    document.getElementById('search-input').dispatchEvent(new Event('search'));
                }, 1000);
            } else {
                showError(result.error || result.message);
            }
        } catch (error) {
            showError('Upload failed: ' + error.message);
        } finally {
            uploadProgress.classList.add('hidden');
            uploadForm.classList.remove('hidden');
            fileInput.value = '';
        }
    }

    function showSuccess(result) {
        uploadResult.className = 'upload-result success';
        uploadResult.innerHTML = `
            <h3>Receipt Analyzed Successfully!</h3>
            <p><strong>Store:</strong> ${result.receipt.transaction_info.store_name}</p>
            <p><strong>Date:</strong> ${result.receipt.transaction_info.date_purchased}</p>
            <p><strong>Total:</strong> $${result.receipt.totals.grand_total.toFixed(2)}</p>
            <p><strong>Items:</strong> ${result.receipt.items.length}</p>
            <button class="view-details-btn" onclick="viewReceipt('${result.receipt_id}')">
                View Full Details
            </button>
        `;
        uploadResult.classList.remove('hidden');
    }

    function showError(message) {
        uploadResult.className = 'upload-result error';
        uploadResult.innerHTML = `
            <h3>Upload Failed</h3>
            <p>${message}</p>
        `;
        uploadResult.classList.remove('hidden');
    }

    // Search input debouncing
    let searchTimeout;
    const searchInput = document.getElementById('search-input');
    const filterInputs = document.querySelectorAll('.filter-item input');

    // Apply debouncing to filter inputs
    filterInputs.forEach(input => {
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                searchInput.dispatchEvent(new Event('search'));
            }, 500);
        });
    });

    // Load initial results (empty search to show all)
    setTimeout(() => {
        searchInput.dispatchEvent(new Event('search'));
    }, 500);
});

// Global function to view receipt details (called from dynamically generated content)
function viewReceipt(receiptId) {
    // This function is defined in index.html template
    // It's duplicated here for reference but the template version takes precedence
    console.log('Viewing receipt:', receiptId);
}
