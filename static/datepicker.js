$('#dp').datepicker({
  onRender: function(date) {    
    var order_dates = "{{ orders|safe }}";

    var clean_order_dates = order_dates.replace(/'/g, '"');
    parsed_order_dates = JSON.parse(clean_order_dates); 

    var primitive_date = date.valueOf();
    var year = date.getFullYear();
    var day = date.getDate();
    var month = (date.getMonth() + 1 );
        
    if (month.toString().length == 1) { month = "0" + month }
    if (day.toString().length == 1) { day = "0" + day }

    var current_date = year + " - "  + day + " - " + month;

    if(jQuery.inArray(current_date, parsed_order_dates) !== -1) { 
        return date.getDate();
        // return date.getMonth();
    } else {        
        return 'disabled'
    }

  }
})

  
$('#dp').datepicker()
  
  
  .on('changeDate', function(ev){
    var href = window.location.protocol + "//" + window.location.host + "/my_orders/" + ev.date.getFullYear() + "-" + ev.date.getDate() + "-" + (ev.date.getMonth() + 1 );
    window.location.replace(href);
    
});