$('#cartModal').on('show.bs.modal', function(e) {
    var table = $("table tbody");    

    function is_plural_small(quantity) {
        if (quantity > 1) { 
            return " små"
        } else if (quantity == 1) { 
            return " lille" 
        }
    };

    function is_plural_large(quantity) {
        if (quantity > 1) { 
            return " store"
        } else if (quantity == 1) { 
            return " stor" 
        }
    };
    
    table.find('tr').each(function (i, el) {
        var $tds = $(this).find('td'),
        row_id = $tds.eq(0).text(),
        product_title = $tds.eq(1).text(),
        price_small = $tds.eq(3).text(),
        price_large = $tds.eq(5).text(),
        quantity_small = document.getElementById('quantity_small_' + row_id.trim());
        quantity_large = document.getElementById('quantity_large_' + row_id.trim());
        
        var large_quantity = ""        
        
        if ( quantity_large != null ) {
            large_quantity = quantity_large.value;            
        };
        
        try {
            if (quantity_small.value != "" || large_quantity != "" ) {
                if (quantity_small.value != 0 || large_quantity != 0) {                    
                    var $modal = $(this);
                                    
                    var table = document.getElementById("modal-table");
                    var row = table.insertRow(-1);
                   
                    var col1 = row.insertCell(0);
                    col1.innerHTML = product_title;
                    // $(col1).attr("id", "no-padding");
                    $(col1).data("id", $tds.parent().attr('id'));


                    if (quantity_small.value != "" && quantity_small.value != 0 && large_quantity != "" && large_quantity != 0) {
                
                        var col2 = row.insertCell(1);
                        $(col2).data("small_quantity", quantity_small.value);
                        $(col2).attr("id", "no-padding");
                        $(col2).data("quantity_id", $tds.parent().attr('id'));
                        col2.innerHTML = quantity_small.value + is_plural_small(quantity_small.value) + " til " + price_small + "kr.";
                       
                        var col3 = row.insertCell(2);
                        $(col3).data("large_quantity", large_quantity);
                        $(col3).attr("id", "no-padding");
                        $(col3).data("quantity_id", $tds.parent().attr('id'));
                        col3.innerHTML = large_quantity + is_plural_large(large_quantity) + " til " + price_large + "kr.";

                    } else if (large_quantity != "" && large_quantity != 0 ) {
                        
                        var col2 = row.insertCell(1);
                        $(col2).data("large_quantity", large_quantity);
                        $(col2).attr("id", "no-padding");
                        $(col2).data("quantity_id", $tds.parent().attr('id'));
                        col2.innerHTML = large_quantity + is_plural_large(large_quantity) + " til " + price_large + "kr";
                        
                        row.insertCell(2)

                    } else if (quantity_small.value != "" && quantity_small.value != 0 ) {
                        
                        var col2 = row.insertCell(1);
                        $(col2).data("small_quantity", quantity_small.value);
                        $(col2).attr("id", "no-padding");
                        $(col2).data("quantity_id", $tds.parent().attr('id'));
                        col2.innerHTML = quantity_small.value + is_plural_small(quantity_small.value) + " til " + price_small + "kr";

                        row.insertCell(2)

                    }


                }
            }
        } catch(err) {}
    }); // end forEach loop.
    
    if ($('#modal-table tr').length == 0 ) {
        // $("#modal-table-container").html("Ingen produkter tilføjet");
        $("#modal-table-container").show();
        $(".order_succes_alert").hide();
        $('.confirm_order_btn').hide();
    }

}) // end show.bs.modal - cartModal

function confirmOrder() {
    console.log("confirmOrder click")
    $('#modal-cart-form').unbind('submit');
    $("#modal-cart-form").submit(function(event) {
        console.log("confirmOrder submit")
        // Stop form from submitting normally                
        event.preventDefault();
        
        var formVals = $("#modal-cart-form").serialize();
            $('#modal-table').find('td').each(function(i, el) {                

                if ( $(this).data('id') != undefined) {
                    formVals += '&' + encodeURIComponent('id' ) + '=' + $(this).data('id');
                } else if ( $(this).data('large_quantity') != undefined) {
                    formVals += '&' + encodeURIComponent('large_quantity_' + $(this).data('quantity_id')) + '=' + $(this).data('large_quantity');
                } else if ( $(this).data('small_quantity') != undefined) {
                    formVals += '&' + encodeURIComponent('small_quantity_' + $(this).data('quantity_id') ) + '=' + $(this).data('small_quantity');
                }

        });        
                
        // Send the data using post
        var posting = $.post($(this).attr('action'), formVals);
        
        
        // if success:
        posting.done(function(data) {
            // success actions, maybe change submit button to 'friend added' or whatever
            
            console.log("success");
            $('.confirm_order_btn').delay( 1000 );
            setTimeout(function() {
                $('.confirm_order_btn').button('reset');
                $('.confirm_order_btn').hide();
                $('.order_succes_alert').fadeIn( 200 );                                
            }, 150);
                        
        });
        
        // if failure:
        posting.fail(function(data) {
            console.log("error")
            $this.button('reset');
            // 4xx or 5xx response, alert user about failure
        });        
    });
}

$('.confirm_order_btn').on('click', function() {   
    var $this = $(this);   
    $this.button('loading');        
});


$('#cartModal').on('hidden.bs.modal', function () {            
    
    $("#modal-table-container").hide();
    $('.confirm_order_btn').show();
    $('.order_succes_alert').hide();
    $("#modal-table tbody").find('tr').each(function (i, el) {         
        el.remove();
    });
});