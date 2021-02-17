var formdata = new FormData();

{% for key, value in data.items() %}
    formdata.append('{{ key }}', '{{ value }}');
{% endfor %}

{% for key, file in files %}
    var file_obj = document.getElementById("{{ loop.index }}_file_upload");
    formdata.append(file_obj.className, file_obj.files[0])
{% endfor %}

var xhr = new XMLHttpRequest()

xhr.open('{{ method }}', '{{ url }}', true)

{% for key, value in headers.items() %}
    xhr.setRequestHeader('{{ key }}', '{{ value }}');
{% endfor %}

xhr.onload = function (e) {
  document.getElementById('response_status').setAttribute('value', xhr.status);

  if(xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
    document.getElementById('response_headers').setAttribute('value', xhr.getAllResponseHeaders());
    document.getElementById('response_content').setAttribute('value', xhr.responseText);
  }
  else{
    document.getElementById('response_headers').setAttribute('value', '');
    document.getElementById('response_content').setAttribute('value', '{"success": false}');
  }

}
xhr.send(formdata);
