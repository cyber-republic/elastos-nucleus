function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$(function(ready) {
    $('#id_select_file').change(function () {
        console.log('change_fired')
        var fileName = $('#id_select_file option:selected').text();
        var csrftoken = getCookie('csrftoken');
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
        $.ajax({
            type: "POST",
            url: 'service/watch_eth_contract',
            data: {
                'file_name': fileName
            },
            success: data => {
                try {
                    console.log(data)
                    var contract_name = data['fields']['contract_name'];
                    var contract_address = data['fields']['contract_address'];
                    var contract_code_hash = data['fields']['contract_code_hash'];
                    $('#id_contract_address').val(contract_address)
                    $('#id_contract_name').val(contract_name)
                    $('#id_contract_code_hash').val(contract_code_hash)
                } catch (err) {
                    console.log("Object did not read")
                }
            }

        })
    });
});
