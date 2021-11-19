function loadTable(){
    $(document).ready(function(){
        var colGroup = 7;
        var comp_table = $('#comp_acct_Table').DataTable({
            responsive: true,                       //enables the responsive capabilities
            
            //the ajax section basically denotes what and where the data is
            "ajax": {
                "url": "/setup/comp_accts/list",                 //basically tells js what url to go to in order to retrieve the desired data
                "dataType": "json",                 //format the data will be in
                "dataSrc": "data",                    //stats what the name of the src dir to look in
                "contentType": "application/json"   //pretty much the same as DataType
            },
            //denotes the order of the row length section
            "lengthMenu": [[100, 50, 25, 10, -1], [100, 50, 25, 10, "ALL"]],
            //where we define what data the table should expect. NOTE: Must be in order
            "columns": [
                //The below data column is just used to have the icon for child row display when data goes past the boundaries 
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
                {"data": "_key"},
                {'data': '_user'},
                {"data": "comp_acct_id"},
                {"data": "blocked_by"},
                {"data": "blocked_on"},
                {"data": "status"},
                {"data": "comments"},
            ],
            "columnDefs": [
                {"visible": false, "targets": [2, 3, colGroup]}
            ],
            //reference link: https://datatables.net/examples/advanced_init/row_grouping.html
            'order':  [[colGroup, 'asc']],
            'drawCallback':   function(settings){
                var api = this.api();
                var rows = api.rows( {page: 'current'} ).nodes();
                var last = null;

                //tbh, I kinda just copy pasted and hoped for the best
                //but i believe it is detemining if the next row is in the same group as the current element
                //if it is then dont make another group label, otherwise make another group label
                api.column(colGroup, {page: 'current'} ).data().each( function(group, i){
                    if(last !== group){
                        $(rows).eq(i).before(
                            '<tr class="group"><td colspan="5">'+group+'</td></tr>'
                        );
                        last = group;
                    }
                });
            }
        });


        //when a user clicks on the edit column of a row, this retrieves the data to build out the modal
        $('#comp_acct_Table tbody').on('click', 'td.edit', function () {
            //get the data for the current row
            var tr = $(this).closest('tr');
            var row = comp_table.row( tr );
            var data = row.data();

            //build the modal
            $('.modal-body').html(lets_gooooooo(data));
            //show off them goods
            $('#editModal').modal({show:true});

        });

        //order by grouping
        $('#comp_acct_Table tbody').on('click', 'tr.group', function () {
            var currOrder = comp_table.order()[0];
            if(currOrder[0] === colGroup && currOrder[1] === 'asc'){
                comp_table.order([colGroup, 'desc']).draw();
            }
            else{
                comp_table.order([colGroup, 'asc']).draw();
            }
        });
    });
    
    //builds out the modal in a dynamic~ish fashion
    function lets_gooooooo(data){
        //data is gonna ref the stuff from the currently selected row             
        
        //set the default block status
        var status_val;
        if(data.status == "active"){
            status_val = '<option value="active" selected>Active</option>'+
            '<option value="inactive">Inactive</option>';
        }
        else{
            status_val = '<option value="active">Active</option>'+
            '<option value="inactive" selected>Inactive</option>';
        }

        //return the formated modal
        //damn this is so ugly
        return '<form action="/comp_accts/update" method="POST">'+
            '<div class="form-group">'+
                '<input type="hidden" name="blocked_by" value='+data.blocked_by+'>'+
                '<input type="hidden" name="date_added" value='+data.blocked_on+'>'+
                '<input type="hidden" name="key" value='+data._key+'>'+
                '<label for="comp_acct_id">Entry:</label>'+
                '<input type="text" class="form-control" name="comp_acct_id" id="comp_acct_id" required value="'+data.comp_acct_id+'">'+
            '</div>'+
            '<div class="form-group">'+
                '<label for="status">Status:</label>'+
                '<select class="form-control" name="status" id="status">'+
                    status_val+
                '</select>'+
            '</div>'+
            '<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">'+
                '<tr>'+
                    '<td>Blocked by:</td>'+
                    '<td>'+data.blocked_by+'</td>'+
                '</tr>'+
                '<tr>'+
                    '<td>Date Blocked:</td>'+
                    '<td>'+data.blocked_on+'</td>'+
                '</tr>'+
            '</table>'+
            '<div class="form-group">'+
                '<label for="comments">Comments:</label>'+
                '<textarea class="form-control" rows="3" name="comments" id="comments">'+ data.comments +'</textarea>'+
            '</div>'+

            '<div class="modal-footer">'+
                '<button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>'+
                    '<input class="btn btn-primary" name="action" type="submit" value="Update">'+
                '<button class="btn btn-danger" type="submit" name="action" value="delete" formaction="/comp_accts/update">Remove Entry</button>'+
            '</div>'+
        '</form>';
    }
}
$(window).on("load", loadTable);