document.addEventListener('DOMContentLoaded', function() {
    var currencyInput = document.getElementById('currency-field');
    
    currencyInput.addEventListener('input', function(e) {
        var value = this.value.replace(/\D/g, '');
    
        if (value.length > 0) {
            var formattedValue = formatMoney(value);
            
            this.value = formattedValue;
        }
    });
    
    function formatMoney(value) {
        var amount = parseFloat(value) / 100;
        return amount.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    }
});