function loadingBtn(){
    $(function() {
        $('form').submit(function() {
            if(!$(this).noValidate){
                $('#btnSubmit').prop("disabled", true);
                $('#tempLoad').prop('outerHTML', `<span id='tempLoad' class="spinner-border spinner-border-sm" role="status" aria-hidden="true" style="width: 1.5rem; height: 1.5rem;"></span>  Loading...`);
            }
            else{
                return;
            }
        });
      });
}
$(window).on("load", loadingBtn);
