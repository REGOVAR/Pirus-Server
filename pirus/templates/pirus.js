

function buildProgressBar(percentage, pbTheme, containerId) {
    var container = $("#" + containerId)
    var style="progress-bar "

    if  (pbTheme == "ERROR" || pbTheme == "CANCELED")
        { style += "progress-bar-danger"}
    else if (pbTheme == "DONE" || pbTheme == "UPLOADED" || pbTheme == "CHECKED")
        { style += "progress-bar-success"}
    else if (pbTheme == "PAUSE")
        { style += "progress-bar-warning"}
    else if (pbTheme == "RUNNING" || pbTheme == "UPLOADING")
        { style += "progress-bar-striped active"}
    else if (pbTheme == "WAITING") { style += "progress-bar-warning progress-bar-striped active"}



    html = "<div class='progress'>\
                <div class='" + style + "' role='progressbar' aria-valuenow='" + percentage + "' aria-valuemin='0' aria-valuemax='0' \
                    style='min-width: 2em; width: " + percentage + "%;'>\
                    " + percentage + "% \
                </div>\
            </div>"

    container.html(html)
}


function buildPopup(popupMsg, popupStyle, containerId) {
    var container = $("#" + containerId)
    container.html('<div class="alert alert-' + popupStyle + ' hidden" id="support-alert">' + popupMsg + '</div>')
}

function addFileEntry(fileId) {
    $.ajax({ url: rootURL + "/file/" + fileId, type: "GET"}).done(function(jsonData)
    {

        $("#filesList tr:last").after('<tr id="fileEntry-' + fileId + '"></tr>')
        var percentage = (jsonData["size"] / jsonData["size_total"] * 100).toFixed(2)
        buildProgressBar(percentage, jsonData["status"], "fileEntry-" + fileId)
        $('#filesList').DataTable();
    })
}


function humansize(nbytes)
{
    var suffixes = ['o', 'Ko', 'Mo', 'Go', 'To', 'Po']
    if (nbytes == 0) return '0 o'

    var i = 0
    while (nbytes >= 1024 && i < suffixes.length-1)
    {
        nbytes /= 1024.
        i += 1
    }
    f = Math.round(nbytes * 100) / 100
    return f + " " + suffixes[i]

}