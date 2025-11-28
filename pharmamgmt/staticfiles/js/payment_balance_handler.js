/**
 * Payment Balance Handler
 * Handles small balance scenarios in payment forms
 */

class PaymentBalanceHandler {
    constructor() {
        this.init();
    }

    init() {
        // Bind events when DOM is ready
        document.addEventListener('DOMContentLoaded', () => {
            this.bindEvents();
        });
    }

    bindEvents() {
        // Listen for invoice selection changes
        const invoiceSelect = document.querySelector('#invoice_no, [name="invoice_no"]');
        const amountInput = document.querySelector('#payment_amount, [name="payment_amount"]');
        
        if (invoiceSelect) {
            invoiceSelect.addEventListener('change', () => {
                this.checkInvoiceBalance();
            });
        }

        if (amountInput) {
            amountInput.addEventListener('input', () => {
                this.validatePaymentAmount();
            });
        }

        // Add "Pay Full Balance" button
        this.addPayFullBalanceButton();
    }

    async checkInvoiceBalance() {
        const invoiceNo = document.querySelector('#invoice_no, [name="invoice_no"]')?.value;
        const transactionType = document.querySelector('#transaction_type, [name="transaction_type"]')?.value || 'payment';
        
        if (!invoiceNo) return;

        try {
            const response = await fetch(`/check-invoice-balance/?invoice_no=${invoiceNo}&transaction_type=${transactionType}`);
            const data = await response.json();
            
            if (data.error) {
                this.showBalanceInfo('Error: ' + data.error, 'error');
                return;
            }

            this.displayBalanceInfo(data);
        } catch (error) {
            console.error('Error checking balance:', error);
        }
    }

    displayBalanceInfo(balanceData) {
        const { total, paid, balance, is_small_balance, is_fully_paid } = balanceData;
        
        // Remove existing balance info
        const existingInfo = document.querySelector('.balance-info');
        if (existingInfo) {
            existingInfo.remove();
        }

        // Create balance info display
        const balanceInfo = document.createElement('div');
        balanceInfo.className = 'balance-info alert';
        
        if (is_fully_paid) {
            balanceInfo.className += ' alert-success';
            balanceInfo.innerHTML = `
                <strong>✅ Invoice Fully Paid</strong><br>
                Total: ₹${total.toFixed(2)} | Paid: ₹${paid.toFixed(2)}
            `;
        } else if (is_small_balance) {
            balanceInfo.className += ' alert-warning';
            balanceInfo.innerHTML = `
                <strong>⚠️ Small Balance Detected</strong><br>
                Total: ₹${total.toFixed(2)} | Paid: ₹${paid.toFixed(2)} | Balance: ₹${balance.toFixed(2)}<br>
                <small>This small balance can be automatically adjusted or written off.</small>
            `;
        } else {
            balanceInfo.className += ' alert-info';
            balanceInfo.innerHTML = `
                <strong>💰 Invoice Balance</strong><br>
                Total: ₹${total.toFixed(2)} | Paid: ₹${paid.toFixed(2)} | Balance: ₹${balance.toFixed(2)}
            `;
        }

        // Insert after invoice selection
        const invoiceField = document.querySelector('#invoice_no, [name="invoice_no"]')?.closest('.form-group');
        if (invoiceField) {
            invoiceField.insertAdjacentElement('afterend', balanceInfo);
        }

        // Update amount field with balance
        const amountInput = document.querySelector('#payment_amount, [name="payment_amount"]');
        if (amountInput && !is_fully_paid) {
            amountInput.value = balance.toFixed(2);
            amountInput.setAttribute('max', balance.toFixed(2));
        }
    }

    addPayFullBalanceButton() {
        const amountInput = document.querySelector('#payment_amount, [name="payment_amount"]');
        if (!amountInput) return;

        // Create button
        const payFullButton = document.createElement('button');
        payFullButton.type = 'button';
        payFullButton.className = 'btn btn-sm btn-outline-primary ml-2';
        payFullButton.innerHTML = '💰 Pay Full Balance';
        payFullButton.onclick = () => this.payFullBalance();

        // Add button next to amount input
        const amountGroup = amountInput.closest('.form-group') || amountInput.parentElement;
        if (amountGroup) {
            amountGroup.appendChild(payFullButton);
        }
    }

    async payFullBalance() {
        const invoiceNo = document.querySelector('#invoice_no, [name="invoice_no"]')?.value;
        const transactionType = document.querySelector('#transaction_type, [name="transaction_type"]')?.value || 'payment';
        const amountInput = document.querySelector('#payment_amount, [name="payment_amount"]');
        
        if (!invoiceNo || !amountInput) return;

        try {
            const response = await fetch(`/check-invoice-balance/?invoice_no=${invoiceNo}&transaction_type=${transactionType}`);
            const data = await response.json();
            
            if (data.error) {
                alert('Error: ' + data.error);
                return;
            }

            if (data.is_fully_paid) {
                alert('Invoice is already fully paid!');
                return;
            }

            amountInput.value = data.balance.toFixed(2);
            
            if (data.is_small_balance) {
                const writeOff = confirm(
                    `This invoice has a small balance of ₹${data.balance.toFixed(2)}. ` +
                    'Would you like to write off this small amount?'
                );
                
                if (writeOff) {
                    // Add hidden field for write-off
                    let writeOffField = document.querySelector('[name="write_off_balance"]');
                    if (!writeOffField) {
                        writeOffField = document.createElement('input');
                        writeOffField.type = 'hidden';
                        writeOffField.name = 'write_off_balance';
                        document.querySelector('form').appendChild(writeOffField);
                    }
                    writeOffField.value = 'true';
                }
            }
        } catch (error) {
            console.error('Error getting balance:', error);
            alert('Error getting invoice balance');
        }
    }

    validatePaymentAmount() {
        const amountInput = document.querySelector('#payment_amount, [name="payment_amount"]');
        if (!amountInput) return;

        const amount = parseFloat(amountInput.value);
        const maxAmount = parseFloat(amountInput.getAttribute('max'));

        if (maxAmount && amount > maxAmount) {
            this.showBalanceInfo(
                `⚠️ Payment amount (₹${amount.toFixed(2)}) exceeds balance (₹${maxAmount.toFixed(2)})`,
                'warning'
            );
        } else {
            // Remove warning if amount is valid
            const existingWarning = document.querySelector('.amount-warning');
            if (existingWarning) {
                existingWarning.remove();
            }
        }
    }

    showBalanceInfo(message, type = 'info') {
        // Remove existing messages
        const existing = document.querySelector('.amount-warning');
        if (existing) {
            existing.remove();
        }

        // Create new message
        const messageDiv = document.createElement('div');
        messageDiv.className = `amount-warning alert alert-${type} mt-2`;
        messageDiv.innerHTML = message;

        // Insert after amount input
        const amountInput = document.querySelector('#payment_amount, [name="payment_amount"]');
        if (amountInput) {
            amountInput.closest('.form-group')?.appendChild(messageDiv);
        }
    }
}

// Initialize when script loads
new PaymentBalanceHandler();