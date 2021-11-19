function loadTable(){
    $(document).ready(function(){
        var colGroup = 4;
        var comp_table = $('#public_ips_Table').DataTable({
            responsive: true,                       //enables the responsive capabilities
            fixedColumns: true,
            initComplete: function () {
                //to apply this to every column, then leave it as columns()
                //to specify which columns to apply, do columns(2,3,5)
                this.api().columns([8,10,11]).every( function () {  
                    var column = this;
                    var select = $('<select><option value=""></option></select>')
                        .appendTo( $(column.footer()).empty() )
                        .on( 'change', function () {
                            var val = $.fn.dataTable.util.escapeRegex(
                                $(this).val()
                            );
                            column
                                .search( val ? '^'+val+'$' : '', true, false )
                                .draw();
                        } );
    
                    column.data().unique().sort().each( function ( d, j ) {
                        select.append( '<option value="'+d+'">'+d+'</option>' )
                    } );
                } );
            },

            //the ajax section basically denotes what and where the data is
            "ajax": {
                "url": "/setup/public_ips/list",                 //basically tells js what url to go to in order to retrieve the desired data
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
                {"data": "ID"},
                {"data": "IP_Address"},
                {"data": "VRF"},
                {"data": "College_Dept_Group"},
                
                {"data": "Vulnerability"},
                {"data": "Contact_Info"},
                {"data": "Contacted"},
                {"data": "Tenable_Agent"},
                {"data": "Comments"},
                {"data": "DNS_concat"},
                {"data": "OS_concat"},
                {"data": "Description"},
                {"data": "DistinguishedName"},
                {"data": "EMailID"},
                {"data": "Model"},
                {"data": "OU"},
                {"data": "UserName"},
                // {"data": "Status"},
                {"data": "hostname"}
            ],
            dom: 'lBfrtip',
            buttons: [
                'csv', 'colvis'
            ],

            "columnDefs": [
                {"visible": false, "targets": [2, 3, 6]}
            ],
            //reference link: https://datatables.net/examples/advanced_init/row_grouping.html
            'order':  [[colGroup, 'asc']],
            // 'drawCallback':   function(settings){
            //     var api = this.api();
            //     var rows = api.rows( {page: 'current'} ).nodes();
            //     var last = null;

            //     //tbh, I kinda just copy pasted and hoped for the best
            //     //but i believe it is detemining if the next row is in the same group as the current element
            //     //if it is then dont make another group label, otherwise make another group label
            //     api.column(colGroup, {page: 'current'} ).data().each( function(group, i){
            //         if(last !== group){
            //             $(rows).eq(i).before(
            //                 '<tr class="group"><td colspan="5">'+group+'</td></tr>'
            //             );
            //             last = group;
            //         }
            //     });
            // }
        });


        //when a user clicks on the edit column of a row, this retrieves the data to build out the modal
        $('#public_ips_Table tbody').on('click', 'td.edit', function () {
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
        $('#public_ips_Table tbody').on('click', 'tr.group', function () {
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
        
        // deprecated field
        // // set arrays for the selected vars then loop through and check if selected, if not then leave out the selected string from the options and then append to string var
        // var status_modal; //will contain the status section of the modal
        // var status_list = ["In Progress", "Done", "Network Gear", "Needs Attention", "MC", "Not Started"]
        // for (let i in status_list){
        //     // add selected attribute if present in the data "Status" field
        //     if (status_list[i] == data['Status']){
        //         status_modal+='<option value="'+status_list[i]+'" selected>'+status_list[i]+'</option>'
        //     }
        //     else{
        //         status_modal+='<option value="'+status_list[i]+'" >'+status_list[i]+'</option>'
        //     }
        // }

        // for the Vulnerability field
        var vuln_modal; //will contain the vuln section of the modal
        var vuln_list = ["Info", "Low", "Medium", "High", "Critical"]
        for (let i in vuln_list){
            // add selected attribute if present in the data "Vulnerability" field
            if (vuln_list[i] == data['Vulnerability']){
                vuln_modal+='<option value="'+vuln_list[i]+'" selected>'+vuln_list[i]+'</option>'
            }
            else{
                vuln_modal+='<option value="'+vuln_list[i]+'" >'+vuln_list[i]+'</option>'
            }
        }

        // for the Contacted field
        var contact_modal; //will contain the vuln section of the modal
        var contact_list = ["TRUE", "FALSE"]
        for (let i in contact_list){
            // add selected attribute if present in the data "Contacted" field
            if (contact_list[i] == data['Contacted']){
                contact_modal+='<option value="'+contact_list[i]+'" selected>'+contact_list[i]+'</option>'
            }
            else{
                contact_modal+='<option value="'+contact_list[i]+'" >'+contact_list[i]+'</option>'
            }
        }

        // for the Tenable_Agent field
        var agent_modal; //will contain the vuln section of the modal
        var agent_list = ["TRUE", "FALSE"]
        for (let i in agent_list){
            // add selected attribute if present in the data "Tenable_Agent" field
            if (agent_list[i] == data['Tenable_Agent']){
                agent_modal+='<option value="'+agent_list[i]+'" selected>'+agent_list[i]+'</option>'
            }
            else{
                agent_modal+='<option value="'+agent_list[i]+'" >'+agent_list[i]+'</option>'
            }
        }

        var col_heads = ["ID", "VRF", "DNS_concat", "OS_concat", "Description", "DistinguishedName", "EMailID", "Model", "OU", "UserName", "hostname"]

        // loop through col heads and add to a var to send over to the python side
        var the_rest = "";
        var i;
        for(i = 0; i < col_heads.length; i++){
            the_rest = the_rest + '<input type="hidden" name="'+col_heads[i]+'" value="'+data[col_heads[i]]+'">'
        }


        //return the formated modal
        return '<form action="/public_ips/update" method="POST">'+
            '<div class="form-group">'+
                '<input type="hidden" name="key" value='+data._key+'>'+
                the_rest+
                '<label for="public_ip_input_modal">Public IP:</label>'+
                '<input type="text" class="form-control" name="public_ip_input_modal" id="public_ip_input_modal" required value="'+data["IP_Address"]+'">'+
            '</div>'+
            '<div class="form-group">'+
                '<label for="vuln_modal">Vulnerability:</label>'+
                '<select class="form-control" name="vuln_modal" id="vuln_modal">'+
                    vuln_modal+
                '</select>'+
            '</div>'+

            '<div class="form-group">'+
                '<label for="contacted_modal">Contacted:</label>'+
                '<select class="form-control" name="contacted_modal" id="contacted_modal">'+
                    contact_modal+
                '</select>'+
            '</div>'+
            '<div class="form-group">'+
                '<label for="tenable_modal">Tenable Agent Installed:</label>'+
                '<select class="form-control" name="tenable_modal" id="tenable_modal">'+
                    agent_modal+
                '</select>'+
            '</div>'+

            '<div class="form-group">'+
                '<label for="group_modal">College_Dept_Group:</label>'+
                '<input type="text" class="form-control" name="group_modal" id="group_modal" value="'+ data['College_Dept_Group'] +'">'+
            '</div>'+
            '<div class="form-group">'+
                '<label for="contact_info_modal">Contact_Info:</label>'+
                '<input type="text" class="form-control" name="contact_info_modal" id="contact_info_modal" value="'+ data["Contact_Info"] +'">'+
            '</div>'+
            '<div class="form-group">'+
                '<label for="comments">Comments:</label>'+
                '<input type="text" class="form-control" name="comments" id="comments" value="'+ data['Comments'] +'">'+
            '</div>'+

            '<div class="modal-footer">'+
                '<button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>'+
                    '<input class="btn btn-primary" name="action" type="submit" value="Update">'+
                '<button class="btn btn-danger" type="submit" name="action" value="delete" formaction="/public_ips/update">Remove Entry</button>'+
            '</div>'+
        '</form>';
    }
}
$(window).on("load", loadTable);