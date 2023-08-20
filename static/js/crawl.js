
function initiateCrawl() {
    var queryParams = new URLSearchParams(window.location.search);
    var crawler_id = queryParams.get('crawler_id')
    toggleCrawlingButton(true)
    callApiRecursively(crawler_id)
}

async function callApiRecursively(crawler_id) {
    try {
        var path = "/api/v1/download/?crawler_id=".concat(crawler_id)
        var url = getUrlFromPath(path)
        const response = await fetch(url);
        const data = await response.json();
        if (data.has_finished) {
        // Finshed Crawling
        toggleCrawlingButton(false);
        console.log('API has finished processing:' + data.has_finished);
        } else if (data.is_blocked) {
            if (data.is_retrying) {
            // Retrying request
            notifyInvalidResponse(data.url, "retry");
            dequeue();
            enqueue(data.url);
            await callApiRecursively(crawler_id);
            } else {
            // Rejected request
            notifyInvalidResponse(data.url, "rejected");
            dequeue()
            await callApiRecursively(crawler_id);
            }
        }
        else {
        addProductRow(data.parsed_data);
        dequeue();
        await new Promise(resolve => setTimeout(resolve, 1));
        await callApiRecursively(crawler_id); // Recursively call the function
        }
    } catch (error) {
        console.log("ERROR " + error)
        console.error('Error calling API:' + error);
        toggleCrawlingButton(false);
    }
}

function notifyInvalidResponse(url, notification_type) {
    var bannerName = "retryWarning";
    var urlBanner = "retriedUrl";
    if (notification_type == "rejected") {
      var bannerName = "rejectError";
      var urlBanner = "rejectedUrl";
    }
    var notification = document.getElementById(bannerName);
    var retriedUrl = document.getElementById(urlBanner);
    retriedUrl.innerHTML = url;
    notification.style.display = 'block';
    setTimeout(function() {
      notification.style.display = 'none';
      retriedUrl.innerHTML = "";
    }, 2000);
}

function createUrlQueueDisplay(crawler_id) {
    const path = "/api/v1/urls/?crawler_id=".concat(crawler_id)
    const url = getUrlFromPath(path)
    fetch(url)
    .then(response => response.json())
    .then(data => {
    data.urls.every(url => {
        enqueue(url)
        return true;
    })

    })
    .catch(error => {
    console.error('Error:', error);
    });
}

function enqueue(url) {
    var ul = document.getElementById("urlQueue");
    var li = document.createElement("li");
    var anch = document.createElement('a')
    li.className = "urlQueue-item"
    li.appendChild(document.createTextNode(url));
    ul.appendChild(li);
}

function dequeue() {
    var node_to_delete = document.getElementsByClassName("urlQueue-item");
    if (node_to_delete.length > 0) {
      node_to_delete[0].remove()
    }
}

function createDataDisplay() {
    $('#product_data_table').DataTable({
      pageLength: 6, responsive: true,
      dom: 'Bfrtip', // Show only buttons in the DOM
      buttons: [
          'csv', 'excel', 'pdf',
      ],
      columnDefs: [
        {
          targets: 0, // First column
          render: function(data, type, row) {
              if (type === 'display') {
                  return `<a href="${data}" target="_blank">${truncateText(data)}</a>`;
              }
              return data;
          }
        },
        {
          targets: '_all',
          render: function(data, type, row) {
            if (type === 'display') {
              return truncateText(data);
            }
            return data;
          }
        }
      ]
    });
}

function addProductRow(data) {
    var table = $('#product_data_table').DataTable();

    var newRowData = [
      data.url, data.name, data.asin, data.brand, data.price, data.average_rating,
      data.review_count, data.short_description, data.images
    ];
    table.row.add(newRowData).draw();
}

function truncateText(text) {
    var maxLength = 50;
    if (text.length > maxLength) {
      return `<span class="truncate" title="${text}">${text.substring(0, maxLength)}...</span>`;
    }
    return text;
}

function getUrlFromPath(path) {
    const currentHost = window.location.host;
    const url = new URL(path, `http://${currentHost}`);
    return url.href
}


function toggleCrawlingButton(isCrawling) {
    var button = document.getElementById('crawlButton');

    if (isCrawling) {
        button.innerHTML = `
            <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            Crawling ...
        `;
        button.classList.remove('btn-success');
        button.classList.add('btn-primary');
        button.disabled = true;
    } else {
        button.innerHTML = 'Start Crawler';
        button.classList.remove('btn-primary');
        button.classList.add('btn-success');
        button.disabled = false;
    }
}