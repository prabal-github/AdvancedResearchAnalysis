/**
 * Email Role Conflict Validation for Registration Forms
 * Add this script to investor and analyst registration forms
 */

function setupEmailValidation(emailInputId, roleType, messageContainerId) {
    const emailInput = document.getElementById(emailInputId);
    const messageContainer = document.getElementById(messageContainerId);
    let validationTimeout;

    if (!emailInput) {
        console.error('Email input element not found:', emailInputId);
        return;
    }

    // Create message container if it doesn't exist
    if (!messageContainer) {
        const container = document.createElement('div');
        container.id = messageContainerId;
        container.className = 'email-validation-message';
        container.style.marginTop = '5px';
        container.style.fontSize = '14px';
        emailInput.parentNode.insertBefore(container, emailInput.nextSibling);
    }

    emailInput.addEventListener('input', function() {
        const email = this.value.trim();
        
        // Clear previous timeout
        if (validationTimeout) {
            clearTimeout(validationTimeout);
        }

        // Clear message if email is empty
        if (!email) {
            clearValidationMessage();
            return;
        }

        // Validate email format first
        if (!isValidEmail(email)) {
            showValidationMessage('Please enter a valid email address', 'warning');
            return;
        }

        // Set timeout for API call (debounce)
        validationTimeout = setTimeout(() => {
            checkEmailConflict(email, roleType);
        }, 500);
    });

    function checkEmailConflict(email, role) {
        const messageDiv = document.getElementById(messageContainerId) || 
                          document.querySelector('.email-validation-message');
        
        if (!messageDiv) return;

        // Show loading message
        showValidationMessage('Checking email availability...', 'info');

        fetch('/api/check-email-conflict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                role: role
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.conflict) {
                showValidationMessage(data.message, 'error');
                emailInput.setCustomValidity(data.message);
            } else {
                showValidationMessage('✓ Email is available', 'success');
                emailInput.setCustomValidity('');
            }
        })
        .catch(error => {
            console.error('Email validation error:', error);
            showValidationMessage('Unable to verify email. Please try again.', 'warning');
            emailInput.setCustomValidity('');
        });
    }

    function showValidationMessage(message, type) {
        const messageDiv = document.getElementById(messageContainerId) || 
                          document.querySelector('.email-validation-message');
        
        if (!messageDiv) return;

        messageDiv.textContent = message;
        messageDiv.className = `email-validation-message ${type}`;
        
        // Apply styles based on type
        switch(type) {
            case 'error':
                messageDiv.style.color = '#dc3545';
                messageDiv.style.backgroundColor = '#f8d7da';
                messageDiv.style.border = '1px solid #f5c6cb';
                break;
            case 'success':
                messageDiv.style.color = '#155724';
                messageDiv.style.backgroundColor = '#d4edda';
                messageDiv.style.border = '1px solid #c3e6cb';
                break;
            case 'warning':
                messageDiv.style.color = '#856404';
                messageDiv.style.backgroundColor = '#fff3cd';
                messageDiv.style.border = '1px solid #ffeaa7';
                break;
            case 'info':
                messageDiv.style.color = '#0c5460';
                messageDiv.style.backgroundColor = '#d1ecf1';
                messageDiv.style.border = '1px solid #bee5eb';
                break;
        }
        
        messageDiv.style.padding = '8px 12px';
        messageDiv.style.borderRadius = '4px';
        messageDiv.style.display = 'block';
    }

    function clearValidationMessage() {
        const messageDiv = document.getElementById(messageContainerId) || 
                          document.querySelector('.email-validation-message');
        
        if (messageDiv) {
            messageDiv.textContent = '';
            messageDiv.style.display = 'none';
        }
        
        emailInput.setCustomValidity('');
    }

    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
}

// Usage examples:
// For investor registration: setupEmailValidation('email', 'investor', 'email-validation-message');
// For analyst registration: setupEmailValidation('email', 'analyst', 'email-validation-message');

// Auto-setup if specific elements are found
document.addEventListener('DOMContentLoaded', function() {
    // Auto-detect registration forms and setup validation
    
    // Check for investor registration form
    const investorEmailInput = document.querySelector('form[action*="investor"] input[name="email"], form[action*="register/investor"] input[name="email"], #investor-email');
    if (investorEmailInput) {
        investorEmailInput.id = investorEmailInput.id || 'investor-email';
        setupEmailValidation(investorEmailInput.id, 'investor', 'investor-email-validation');
    }
    
    // Check for analyst registration form
    const analystEmailInput = document.querySelector('form[action*="analyst"] input[name="email"], form[action*="register/analyst"] input[name="email"], #analyst-email');
    if (analystEmailInput) {
        analystEmailInput.id = analystEmailInput.id || 'analyst-email';
        setupEmailValidation(analystEmailInput.id, 'analyst', 'analyst-email-validation');
    }
    
    // Generic email input in registration forms
    const genericEmailInput = document.querySelector('input[name="email"][type="email"]');
    if (genericEmailInput && !investorEmailInput && !analystEmailInput) {
        // Try to determine role from URL or form action
        const currentPath = window.location.pathname;
        const formAction = genericEmailInput.closest('form')?.action || '';
        
        let role = '';
        if (currentPath.includes('investor') || formAction.includes('investor')) {
            role = 'investor';
        } else if (currentPath.includes('analyst') || formAction.includes('analyst')) {
            role = 'analyst';
        }
        
        if (role) {
            genericEmailInput.id = genericEmailInput.id || `${role}-email`;
            setupEmailValidation(genericEmailInput.id, role, `${role}-email-validation`);
        }
    }
});