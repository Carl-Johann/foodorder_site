function order(col) {                                
    
    var $sort = this;            
    var $table = $('#sort-table');
    var $rows = $('tbody > tr', $table);
    
        var status = ""
        if ($("#sort-table").attr("data-sort-order") == "asc") {
            status = "desc";
            $("#sort-table").attr("data-sort-order", "desc");
        } else if ($("#sort-table").attr("data-sort-order") == "desc") {
            status = "asc";
            $("#sort-table").attr("data-sort-order", "asc");
        }
        

    $rows.sort(function(a, b) {
        var keyA = $('td:eq(' + col + ')', a).text();
        var keyB = $('td:eq(' + col + ')', b).text();
             
        if (status == "asc") {
            return (keyA < keyB) ? 1 : -1 
        } else if (status == "desc") {
            return (keyA > keyB) ? 1 : -1;
        }
        
    });
    
    
    var numArray = $rows
    
    if (col == 0){
        numArray = $rows.sort(function (a, b) {  
            var keyA = $('td:eq(' + col + ')', a).text();
            var keyB = $('td:eq(' + col + ')', b).text();
            return keyA - keyB;  
        });
    }

    $.each(numArray, function(index, row) {            
        $table.append(row);            
    });
    
}


function search_in_product_table() {
  // Declare variables 
  var input, filter, table, tr, td, i;
  input = document.getElementById("search_input");
  filter = input.value.toUpperCase();
  table = document.getElementById("sort-table");
  tr = table.getElementsByTagName("tr");

  // Loop through all table rows, and hide those who don't match the search query
  for (i = 0; i < tr.length; i++) {
    td = tr[i].getElementsByTagName("td")[1];
    if (td) {
      if (td.innerHTML.toUpperCase().indexOf(filter) > -1) {
        tr[i].style.display = "";
      } else {
        tr[i].style.display = "none";
      }
    } 
  }
}


function showCartModal(){
    $('#cartModal .registerBox').fadeOut('fast',function(){
        $('.loginBox').fadeIn('fast');
        $('.register-footer').fadeOut('fast',function(){
            $('.login-footer').fadeIn('fast');    
        });
        
        $('.modal-title').html('Login with');
    });       
     $('.error').removeClass('alert alert-danger').html(''); 
}

function openCartModal(){
    showLoginForm();
    setTimeout(function(){
        $('#cartModal').modal('show');    
    }, 230);
    
}
