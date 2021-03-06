window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        saveLayoutTest: function(saveButClicks, appBody, dataStore) {
            let elements = []
            if (!saveButClicks) {
                return ""
            } else {
                for (i = 0; i < appBody.length; i++) {
                    let id = appBody[i]['props']['id']

                    let curr_child_py = appBody[i]
                    let curr_child_js = $(`#${id}`)
                    
                    let element = {
                        'id': `test-graph${i}`,
                        'top': `${curr_child_js[0]['offsetTop'] / window.innerHeight * 100}%`,
                        'left': `${curr_child_js[0]['offsetLeft'] / window.innerWidth * 100}%`,
                        'height': `${curr_child_js[0]['clientHeight'] / window.innerHeight * 100}%`,
                        'width': `${curr_child_js[0]['clientWidth'] / window.innerWidth * 100}%`,
                        'type': `${curr_child_js[0]['localName']}`,
                        'text': curr_child_js[0].classList.contains('graph') ? '' : curr_child_js[0]['innerText'],
                        'graph': curr_child_js[0].classList.contains('graph'),
                        'layout': curr_child_js[0].classList.contains('graph') ? curr_child_py['props']['children'][1]['props']['figure']['layout'] : '',
                        'data': curr_child_js[0].classList.contains('graph') ? dataStore[id] : ""
                    }

                    elements.push(element)
                }

                return elements
            }
        }
    }
})


window.onload = (event) => {
    console.log('page is fully loaded');

    setTimeout(function(){

        // setting up draggable / resizable for new elements added 
        const config = {attributes: false, childList: true, subtree: false};
        const draggableCallback= function(mutationList, observer) {
            for (const mutation of mutationList){
                if (mutation.type === 'childList') {
                    $(".draggable").draggable();
                    $(".draggable").resizable();
                    $(".draggable").addClass('absolute');
                }
            }

        }

        const observer = new MutationObserver(draggableCallback)
        observer.observe(document.getElementById('body'), config)

        // draggable and resizable for existing elements
        $(".draggable").draggable();
        $(".draggable").resizable();
        $(".draggable").addClass('absolute');

        $('.ui-resizable-handle').mouseup(function() {
            let parent = $(this).parent()

            parent.width(`${parent[0]['clientWidth'] / window.innerWidth * 100}%`)
            parent.height(`${parent[0]['clientHeight'] / window.innerHeight * 100}%`)
        })

        $('.draggable').mouseup(function() {
            $(this).css('left', `${$(this)[0]['offsetLeft'] / window.innerWidth * 100}%`)
            $(this).css('top',`${$(this)[0]['offsetTop'] / window.innerHeight * 100}%`)
        })

    }, 1000);
};