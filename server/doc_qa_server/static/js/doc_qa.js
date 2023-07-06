
//func


//click event
var when_click_search = function () {

  var element_search_button = $("#search");

  if (element_search_button.text() === "running") {
    alert("please wait this running finish.")
    return null;
  }

  //var
  var engine_name = $("#select_engine_name").val();
  var file_url = $("#file_url").val();
  var query = $("#query").val();
  var top_k = $("#top_k").val();
  var chunk_size = $("#chunk_size").val();
  var chunk_overlap = $("#chunk_overlap").val();

  var url = "single_doc_qa/retrieval_qa_chain";

  element_search_button.text("running");
  $.ajax({
    async: true,
    type: "POST",
    url: url,
    data: {
      engine_name: engine_name,
      file_url: file_url,
      query: query,
      top_k: top_k,
      chunk_size: chunk_size,
      chunk_overlap: chunk_overlap,
    },
    success: function (js, status) {
      //log
      console.log(`url: ${url}, status: ${status}, js: ${js}`);
      element_search_button.text("search");

      //answer
      var element_answer = $("#answer")
      element_answer.text(js.result.result)

      //documents
      var element_documents = $("#documents")
      element_documents.empty();
      for (var i = 0; i < js.result.source_documents.length; i++) {
        element_documents.append(`<div id="document_${i}" class="document_list"></div>`)
        $('#document_'+[i]).html(js.result.source_documents[i])
      }
    },
    error: function (js, status) {
      console.log(`url: ${url}, status: ${status}, js: ${js}`);
      element_search_button.text("search");
      alert(js.message)
    }
  });
}


//reset messages
var reset_choice_of_engine_name = function() {
  var url = "single_doc_qa/get_choice_of_engine";

  $.ajax({
    async: true,
    type: "GET",
    url: url,
    data: {},
    success: function (js, status) {
      //log
      console.log("url: " + url + ", status: " + status + ", js: " + js);

      //var
      var element_select_engine_name = $("#select_engine_name")

      //reset language_choices
      element_select_engine_name.empty();
      for (var i = 0; i < js.result.length; i++) {
        element_select_engine_name.append("<option>" + js.result[i] + "</option>")
      }
    }
  });
}


$(document).ready(function(){
  reset_choice_of_engine_name();

  $("#search").click(function(){
    when_click_search();
  });

})
