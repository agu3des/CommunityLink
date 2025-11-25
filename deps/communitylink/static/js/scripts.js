/**
 * CommunityLink Scripts
 * Main JavaScript file for the application
 * Handles custom form inputs, select dropdowns, and date inputs
 */

document.addEventListener('DOMContentLoaded', function() {
    // ===== Customize category select with green hover effect =====
    const categorySelects = document.querySelectorAll('select[name="categoria"], select#categoria');
    
    categorySelects.forEach(select => {
        // Hide the native select
        select.style.display = 'none';
        
        // Create a container div for the custom select
        const container = document.createElement('div');
        container.className = 'custom-select-container';
        container.style.position = 'relative';
        container.style.display = 'inline-block';
        container.style.width = '100%';
        
        // Insert container before select
        select.parentNode.insertBefore(container, select);
        container.appendChild(select);
        
        // Create a button that displays the selected option
        const button = document.createElement('button');
        button.className = 'custom-select-button';
        button.type = 'button';
        button.style.width = '100%';
        button.style.padding = '0.375rem 0.75rem';
        button.style.backgroundColor = '#f9fafb';
        button.style.border = '1px solid #e5e7eb';
        button.style.borderRadius = '6px';
        button.style.fontSize = '1rem';
        button.style.textAlign = 'left';
        button.style.cursor = 'pointer';
        button.style.appearance = 'none';
        button.style.transition = 'border-color .12s ease, background .12s ease';
        button.textContent = select.options[select.selectedIndex].text;
        container.insertBefore(button, select);
        
        // Create a custom dropdown list
        const customList = document.createElement('div');
        customList.className = 'custom-select-list';
        customList.style.display = 'none';
        customList.style.position = 'absolute';
        customList.style.top = '100%';
        customList.style.left = '0';
        customList.style.right = '0';
        customList.style.backgroundColor = '#fff';
        customList.style.border = '1px solid #e6e9ef';
        customList.style.borderRadius = '6px';
        customList.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
        customList.style.zIndex = '1000';
        customList.style.maxHeight = '300px';
        customList.style.overflowY = 'auto';
        customList.style.marginTop = '4px';
        
        container.appendChild(customList);
        
        // Populate custom list with options
        function populateCustomList() {
            customList.innerHTML = '';
            Array.from(select.options).forEach((option, index) => {
                const item = document.createElement('div');
                item.className = 'custom-select-item';
                item.textContent = option.text;
                item.style.padding = '0.6rem 0.75rem';
                item.style.cursor = 'pointer';
                item.style.color = '#111827';
                item.style.borderBottom = '1px solid rgba(15,23,42,0.04)';
                item.style.transition = 'background .12s ease, color .12s ease';
                
                if (option.selected) {
                    item.style.backgroundColor = '#ecfdf5';
                    item.style.color = '#15803d';
                    item.style.fontWeight = '600';
                }
                
                item.addEventListener('mouseover', function() {
                    item.style.backgroundColor = '#15803d';
                    item.style.color = '#ffffff';
                });
                
                item.addEventListener('mouseout', function() {
                    if (option.selected) {
                        item.style.backgroundColor = '#ecfdf5';
                        item.style.color = '#15803d';
                    } else {
                        item.style.backgroundColor = '#fff';
                        item.style.color = '#111827';
                    }
                });
                
                item.addEventListener('click', function() {
                    select.value = option.value;
                    button.textContent = option.text;
                    customList.style.display = 'none';
                    populateCustomList();
                    select.dispatchEvent(new Event('change'));
                });
                
                customList.appendChild(item);
            });
        }
        
        // Show/hide custom list on button click
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            if (customList.style.display === 'none') {
                customList.style.display = 'block';
                populateCustomList();
            } else {
                customList.style.display = 'none';
            }
        });
        
        select.addEventListener('change', function() {
            customList.style.display = 'none';
            button.textContent = select.options[select.selectedIndex].text;
            populateCustomList();
        });
        
        // Initial populate
        populateCustomList();
        
        // Hide on outside click
        document.addEventListener('click', function(e) {
            if (!container.contains(e.target)) {
                customList.style.display = 'none';
            }
        });
    });

    // ===== Customize date input with enhanced styling =====
    const dateInputs = document.querySelectorAll('input[type="date"]');
    
    dateInputs.forEach(input => {
        // Add custom styling class
        input.classList.add('custom-date-input');
        
        // Create wrapper for better control
        const wrapper = document.createElement('div');
        wrapper.className = 'custom-date-wrapper';
        wrapper.style.position = 'relative';
        wrapper.style.display = 'inline-block';
        wrapper.style.width = '100%';
        
        input.parentNode.insertBefore(wrapper, input);
        wrapper.appendChild(input);
        
        // Add focus and blur events for visual feedback
        input.addEventListener('focus', function() {
            this.style.borderColor = '#15803d';
            this.style.boxShadow = '0 0 0 3px rgba(21, 128, 61, 0.1)';
        });
        
        input.addEventListener('blur', function() {
            this.style.borderColor = '#e5e7eb';
            this.style.boxShadow = 'none';
        });
    });
});
