error_flag = false;
function add_ticket(id){
  $.ajax({
    url: base_url,
    contentType: 'application/json',
    dataType: 'json',
    type:'post',
    data: JSON.stringify(
      {method:'ticket.get', params:[id]}
    ), 
    success: function(data){
     id = data['result'][0]
     content = data['result'][3]
     if(parseInt($('#field-parents').val())==id){
       selected = ' checked' ;
     } else {
       selected = '';
     }
     $('#ticket_list').append('<tr style="border: 1px solid lightgray;height: 1em;"><td style="border: 1px solid lightgray;"><input type=radio id=parent_ticket name=parent_ticket value='+id+selected+' />'+id+'</td><td style="overflow:hidden;border: 1px solid lightgray;">'+content['type']+'</td><td style="overflow:hidden;"style="overflow:hidden;">'+content['summary']+'</td></tr>');
    },
    error: function(data) {
         if(error_flag==false){
             alert("チケットの取得に失敗しました。");
             error_flag=true;
         }

    }
  });
}

function get_ticket_list(milestone,component){
  param = "milestone="+milestone;
  if (component){
     param = param+"&component="+component;
  }

  $.ajax({
    url: base_url,
    contentType: 'application/json',
    dataType: 'json',
    type:'post',
    data: JSON.stringify(
      {method:'ticket.query', params:[param]}
    ), 
    success: function(data){
     if(data==null || data['result']==null){
         if(error_flag==false){
             alert("チケットの取得に失敗しました。チケットをリストから入力するにはXML_RPC権限が必要です。管理者に設定を依頼してください。");
             error_flag=true;
         }
     } else {
         list = data['result'];
         for(i=0;i<list.length;i++){
           add_ticket(list[i]);
         }
     }
    },
    error: function(data) {
       if(error_flag==false){
         if(error_flag==false){
             alert("チケットの取得に失敗しました。チケットをリストから入力するにはXML_RPC権限が必要です。管理者に設定を依頼してください。");
             error_flag=true;
         }
       }
    }
 });
}

$(function(){
   base_url = $("link[rel=tracsubticket.base]").attr("href")+"/login/jsonrpc";

  $("<span />", {
    id:'popup_ticket',
    text:'？',
    click: function(){
      $('#ticket_list').empty();
      get_ticket_list($('#field-milestone').val(),$('#field-component').val());
      $('#dialog-form').dialog('open');
      $('#dialog-form').css({height: '200px'});
    }
  }).insertAfter("#field-parents");

  $('<div id="dialog-form" title="親チケットの選択" style="height: 300px;"><p>親チケットを選択してください</p><table style="border: 1px solid lightgray;width: 95%;border-collapse: collapse;table-layout:fixed;"><thead><th style="border: 1px solid lightgray;width: 3em;">ID</th><th style="border: 1px solid lightgray;width:8em;">種類</th><th style="border: 1px solid lightgray;">概要</th></thead><tbody id="ticket_list"></tbody></table></div>').appendTo("body");
/*
  offset=$('#popup_ticket').offset();
  alert([offset.top,offset.left]);
*/
  $("#dialog-form" ).dialog({
    autoOpen: false,
    resizable: true,
    draggable: false,
    height: '300px',
    width: '500px',
    modal: true,
    position: 'center',
    buttons: {
      "選択": function() {
                t = $('input[name=parent_ticket]:checked').val();
                $('#field-parents').val(t);
                $(this).dialog("close");
              },
      "キャンセル": function() {
        $(this).dialog("close");
      }
    }
  });
  $('div[aria-labelledby=ui-dialog-title-dialog-form]').css({position: 'absolute'});
});

