import {getCookie,csrfSafeMethod} from './utils.js';
import {clearStorage,getAllItemsJSON} from './localstorage.js';

$( document ).ready(function() {

    var lock = function(){
        $('#modal_upload').show();
    }

    var unlock = function(){
        $('#modal_upload').hide();
    }

    var clearInputFile = function(f){
        if(f.value){
            try{
                f.value = ''; //for IE11, latest Chrome/Firefox/Opera...
            }catch(err){
            }
            if(f.value){ //for IE5 ~ IE10
                var form = document.createElement('form'), ref = f.nextSibling;
                form.appendChild(f);
                form.reset();
                ref.parentNode.insertBefore(f,ref);
            }
        }
    }

    var resetInterface = function(){
        clearInputFile( $('#fileinput') );
        $('#model_select').val("");
    }

    var checkInput = function(){
        const items = getAllItemsJSON();
        const file = items.file_path;
        const success = items.success;
        const class_id = items.class_id;
        if(!file){
            toastr.error("Please select a zip file with images to classify.");
            return false;
        }
        if(!class_id){
            toastr.error("Please select a model to classify the images with.");
            return false;
        }
        if(!success){
            toastr.error("The zip file did not upload correctly. Please try again.");
            return false;
        }
        return true;
    }

    var do_classification = function(){
        const all_correct = checkInput();
        const classify_params = getAllItemsJSON();
        if(all_correct){
            $.ajax({
                url: _ajax_classify,  // Make sure this variable is defined
                type: "POST",
                data: JSON.stringify(classify_params),
                processData: false,  // Prevent jQuery from processing the data
                contentType: "application/json; charset=utf-8",
                beforeSend: function(xhr, settings) {
                    lock();
                    if (!csrfSafeMethod(settings.type)) {
                        var csrftoken = getCookie('csrftoken');
                        xhr.setRequestHeader('X-CSRFToken', csrftoken);
                    }
                },
                success: function (response) {
                    console.log(response);
                    unlock();
                    if (response.success) {
                        console.log(response);
                        toastr.success("success!");
                    } else {
                        toastr.error("fail!");
                    }
                },
                error: function () {
                    unlock();
                    toastr.error("Error while uploading!");
                }
            });
        }
    }

    var uploadfile = function(){
        let fileInput = $('#fileinput')[0];
        if (fileInput.files.length === 0) {
            toastr.error("Please select a file.");
            return;
        }

        let file = fileInput.files[0];
        let formData = new FormData();
        formData.append("file", file);

        $.ajax({
            url: _ajax_upload_url,  // Make sure this variable is defined
            type: "POST",
            data: formData,
            processData: false,  // Prevent jQuery from processing the data
            contentType: false,  // Prevent jQuery from setting content type
            beforeSend: function(xhr, settings) {
                lock();
                if (!csrfSafeMethod(settings.type)) {
                    var csrftoken = getCookie('csrftoken');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                }
                //resetInterface();
            },
            /*xhr: function () {
                let xhr = new window.XMLHttpRequest();
                xhr.upload.addEventListener("progress", function (event) {
                    if (event.lengthComputable) {
                        let percent = (event.loaded / event.total) * 100;
                        $("#progress-bar").css("width", percent + "%").text(Math.round(percent) + "%");
                        $("#progress-container").show();
                    }
                }, false);
                return xhr;
            },*/
            success: function (response) {
                console.log(response);
                unlock();
                if (response.success) {
                    toastr.success("File uploaded successfully!");
                    var key;
                    for(key in response){
                        localStorage.setItem(key,response[key]);
                    }
                } else {
                    toastr.error("Upload failed!");
                }
            },
            error: function () {
                unlock();
                toastr.error("Error while uploading!");
            }
        });
    }

    $('#fileinput').on('change', function(){
        uploadfile();
    });


    $('#model_select').on('change', function( evt ){
        $("#card_all").show();
        $("#card_title").text( $(this).find(":selected").val() );
        $("#card_description").text( $(this).find(":selected").data("description") );
        $("#card_runson").text( $(this).find(":selected").data("runson") );
        localStorage.setItem("class_id", $(this).find(":selected").attr("id"));
    });

    $('#run_btn').on('click', function(evt){
        /*toastr.success("running!");
        console.log(getAllItemsJSON());*/
        do_classification();
    });

    resetInterface();
    clearStorage();
});