function loadTable(){
    $(document).ready(function(){        
        var timesheet_Table = $('#timesheet_Table').DataTable({
            responsive: true,                       //enables the responsive capabilities
            
            //the ajax section basically denotes what and where the data is
            "ajax": {
                "url": "/setup/timesheet",                 //basically tells js what url to go to in order to retrieve the desired data
                "dataType": "json",                 //format the data will be in
                "dataSrc": "data",                    //stats what the name of the src dir to look in
                "contentType": "application/json"   //pretty much the same as DataType
            },
            //where we define what data the table should expect. NOTE: Must be in order
            "columns": [
                {
                    "className":      'details-control',
                    "orderable":      false,
                    "data":           null,
                    "defaultContent": '' 
                },
                //used to hold the edit icon
                {
                    "className":      'edit',
                    "orderable":      false,
                    "data":           null,
                    "defaultContent": '<i class="fa fa-edit"></i>'  //for some reason this had to be class="fa fa-edit" and not class="far fa-edit" idk why tho...
                },
                {"data": "id"},
                {"data": "date"},
                {'data': 'start'},
                {"data": "end"},
                {"data": "username"},
                {"data": "comment"},
            ],
            "columnDefs": [
                {"visible": false, "targets": [2, 7]}
            ],

            dom: 'lBfrtip',
            buttons: [
                'csv', 'colvis'
            ]
        });
        //when a user clicks on the edit column of a row, this retrieves the data to build out the modal
        $('#timesheet_Table tbody').on('click', 'td.edit', function () {
            //get the data for the current row
            var tr = $(this).closest('tr');
            var row = timesheet_Table.row( tr );
            var data = row.data();

            var temp_modal = lets_gooooooo(data);
            var modal_get = document.getElementById('editModalbody');
            modal_get.innerHTML =temp_modal;
            //build the modal
            // $('#editModal-body').html(lets_gooooooo(data));
            //show off them goods
            $('#editModal').modal({show:true});
        });
    });
    
    //builds out the modal in a dynamic~ish fashion
    function lets_gooooooo(data){
        var start_conv = time_convert(data.start);
        var end_conv;
        if((data.end.localeCompare("NULL") == 0) || (data.end.localeCompare("") == 0)){
            end_conv = "NULL";
        }
        else{
            end_conv = time_convert(data.end);
        }
        
        //return the formated modal
        //damn this is so ugly
        return '<form action="/timesheet/update" method="POST">'+
            '<div class="form-group">'+
                '<input type="hidden" name="row_id" value="'+data.id+'">'+
                '<input type="hidden" name="date" value="'+data.date+'">'+
            '</div>'+
            '<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">'+
                '<tr>'+
                    '<td>User:</td>'+
                    '<td>'+data.username+'</td>'+
                '</tr>'+
                '<tr>'+
                    '<td>Date:</td>'+
                    '<td>'+data.date+'</td>'+
                '</tr>'+
            '</table>'+
            '<div class="form-group">'+
                '<label for="start" class="col-2 col-form-label">Start</label>'+
                '<div class="col-10">'+
                    '<input class="form-control" name="start" type="time" value="'+start_conv+'" id="start">'+
                '</div>'+
            '</div>'+
            '<div class="form-group">'+
                '<label for="end" class="col-2 col-form-label">End</label>'+
                '<div class="col-10">'+
                    '<input class="form-control" name="end" type="time" value="'+end_conv+'" id="end">'+
                '</div>'+
            '</div>'+

            '<div class="form-group">'+
                '<label for="comment">Comments:</label>'+
                '<textarea class="form-control" rows="3" name="comment" id="comment">'+ data.comment +'</textarea>'+
            '</div>'+

            '<div class="modal-footer">'+
                '<button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>'+
                    '<input class="btn btn-primary" name="action" type="submit" value="Update">'+
                '<button class="btn btn-danger" type="submit" name="action" value="delete" formaction="/timesheet/delete">Remove Entry</button>'+
            '</div>'+
        '</form>';
    }

    // function is used to convert 12 hour format to 24 hour
    function time_convert(time_input){
        // check if the time is in 12 or 24 hour format
        if((/^\d{2}:\d{2}:\d{2} \w{2}/.test(time_input))){
            // should always only have one space hh:mm:ss am/pm
            var time_array = time_input.split(" ", 2);
            var temp_time = time_array[0].split(":", 3);

            time_array = time_array[1].toLowerCase();
            if(temp_time[0].localeCompare('12') == 0){
                temp_time[0] = '00';
            }

            if(time_array.localeCompare("pm") == 0){
                temp_time[0] = parseInt(temp_time[0], 10) + 12;
            }

            var bring_it_back_now = temp_time[0]+':'+temp_time[1];
            return bring_it_back_now;
        }
        else{
            return time_input
        }

    }
}
$(window).on("load", loadTable);