/*
 * jQuery File Upload Plugin JS Example 7.0
 * https://github.com/blueimp/jQuery-File-Upload
 *
 * Copyright 2010, Sebastian Tschan
 * https://blueimp.net
 *
 * Licensed under the MIT license:
 * http://www.opensource.org/licenses/MIT
 */

/*jslint nomen: true, unparam: true, regexp: true */
/*global $, window, document */

$(function () {
    'use strict';

    // Initialize the jQuery File Upload widget:
    $('#fileupload').fileupload({
        // Uncomment the following to send cross-domain cookies:
        //xhrFields: {withCredentials: true},
        url: identity_validation_post, // '/profile/identity_validation',
        dropZone: $('#file_dragzone'),
        // Obtengo el evento de agregado de archivo
        add: function (e, data) {
            $.each(data.files, function (index, file) {
                var obj = addFileToUploadList(file);
                data.context = obj;
                //bind submit to start button
               var jqXHR=null;
               obj.find('.start').click(function(){
                    jqXHR = data.submit();
                    return false;
                }); 
                obj.find('.cancel').click(function (e) {
                    if(jqXHR!=null)
                      jqXHR.abort();
                    $(this).parents('tr')[0].remove();
                    return false;
                });
                //alert('Added file: ' + file.name + '[' + (file.size/1024).toFixed(2) + 'Kb]');
            });
          },
        process: [
                  {
                    action: 'load',
                    fileTypes: /^image\/(gif|jpeg|png)$/,
                    maxFileSize: 2000000 // 2MB
                  },
                  {
                      action: 'save'
                  }
                  ],
        done: function (e, data) {
                //alert('success'+data);
                data.context.find('div.progress:first').parents('tr:first').remove();
                
                $.ajax({
                  type: "GET",
                  cache: false,
                  url: identity_validation_files, // '/profile/profile_form_verification_files',
                  success: (function (data) {
                    $('#verification_files').html(data);
                  }),
                  error: (function (data) {
                   //window.location=identity_validation_post; // '/profile/identity_validation';
                  })
                });
                
                // data.result
                // data.textStatus;
                // data.jqXHR;
              },
        fail: function (e, data) {
                alert('La subida del archivo falló. Actualice la página e inténtelo más tarde.');
                // data.errorThrown
                // data.textStatus;
                // data.jqXHR;
              },
        progress: function (e, data) {
                  console.log(data.context); 
                  var progress = parseInt(data.loaded / data.total * 100, 10);
                  data.context.find('.progress div.bar:first').css(
                  //data.context.find('.js-progress-active').css(
                    'width',
                    progress + '%'
                    ).text(progress + '%');
                // data.errorThrown
                // data.textStatus;
                // data.jqXHR;
              },
        
    });

    function addFileToUploadList(file){
      return $('#files_to_upload').append(
        '<tr class="template-upload fade in">'+
        '    <td class="name"><span>'+file.name+'</span></td>'+
        '    <td class="size"><span>'+(file.size/1024).toFixed(2)+' KB</span></td>'+
        '    <td>'+
        '      <div class="progress progress-success progress-striped active" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><div class="bar" style="width:0%;"></div></div>'+
        '    </td>'+
        '    <td class="cancel">'+
        '      <button class="btn red canceler_button">'+
        '        <i class="icon-ban-circle icon-white"></i>'+
        '        <span>Cancel</span>'+
        '      </button>'+
        '    </td>'+
        '  </tr>');
      
    }
    
    // Enable iframe cross-domain access via redirect option:
    // $('#fileupload').fileupload(
        // 'option',
        // 'redirect',
        // window.location.href.replace(
            // /\/[^\/]*$/,
            // '/cors/result.html?%s'
        // )
    // );

/*    if (window.location.hostname === 'blueimp.github.com') 
    {
        // Demo settings:
        $('#fileupload').fileupload('option', {
            url: '//jquery-file-upload.appspot.com/',
            maxFileSize: 5000000,
            acceptFileTypes: /(\.|\/)(gif|jpe?g|png)$/i,
            process: [
                {
                    action: 'load',
                    fileTypes: /^image\/(gif|jpeg|png)$/,
                    maxFileSize: 20000000 // 20MB
                },
                {
                    action: 'resize',
                    maxWidth: 1440,
                    maxHeight: 900
                },
                {
                    action: 'save'
                }
            ]
        });
        // Upload server status check for browsers with CORS support:
        if ($.support.cors) {
            $.ajax({
                url: '//jquery-file-upload.appspot.com/',
                type: 'HEAD'
            }).fail(function () {
                $('<span class="alert alert-error"/>')
                    .text('Upload server currently unavailable - ' +
                            new Date())
                    .appendTo('#fileupload');
            });
        }
    } else {
        // Load existing files:
        $.ajax({
            // Uncomment the following to send cross-domain cookies:
            //xhrFields: {withCredentials: true},
            url: $('#fileupload').fileupload('option', 'url'),
            dataType: 'json',
            context: $('#fileupload')[0]
        }).done(function (result) {
            $(this).fileupload('option', 'done')
                .call(this, null, {result: result});
        });
    }
*/
});
