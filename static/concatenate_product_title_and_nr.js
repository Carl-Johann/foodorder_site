$window_width = $( window ).width();

if ($window_width <= 678) {                    
    concatenate_nr_and_product_title()
}    

function concatenate_nr_and_product_title() {
    
    var $table = $('.table');            
    var $rows = $('tbody > tr', $table);        
    var product_title_th = $('th:eq(1)', 0)

    if (product_title_th.text() != "Nr & Produkt" && $window_width <= 678) {            
        product_title_th.html("Nr & Produkt");

        $rows.each(function(index, row) {
            var product_nr = $('td:eq(0)', row);
            var product_title = $('td:eq(1)', row);
            
            if ($(row).attr('id') != "to_not_concatenate") {                
                new_title = product_nr.text() + "-" + product_title.text();
                product_title.html(new_title);
                $(product_title).css('font-size', '13px');
            }

        });
        
    } else if (product_title_th.text() == "Nr & Produkt" && $window_width >= 678) {            
        product_title_th.html("Produkt");

        $rows.each(function(index, row) {
            var product_nr = $('td:eq(0)', row);
            var product_title = $('td:eq(1)', row);
            
            index_of_title_to_remove = product_title.text().indexOf("-");
            new_title = product_title.text().slice(index_of_title_to_remove + 1);
            
            product_title.html(new_title);
            $(product_title).css('font-size', '14px');
        });

    }
}

$( window ).resize(function() {
    $window_width = $( window ).width();        
    concatenate_nr_and_product_title();        
});