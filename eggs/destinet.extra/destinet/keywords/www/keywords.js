if (toggleSelect == undefined) {
    var isSelected = false;

    var toggleSelect = function() {
        var frm = document.frmAllocateKeywords;
        if(frm == undefined){
            var frm = document.objectItems;
        }

        if(frm != undefined){
            var i;

            if (isSelected == false) {
                for(i=0; i<frm.elements.length; i++){
                    if (frm.elements[i].type == "checkbox" && ((frm.elements[i].name == 'checked_paths:list') || (frm.elements[i].name == 'id:list'))) {
                        frm.elements[i].checked = true;
                    }
                }
                isSelected = true;
            }else {
                for(i=0; i<frm.elements.length; i++){
                    if (frm.elements[i].type == "checkbox" && ((frm.elements[i].name == 'checked_paths:list') || (frm.elements[i].name == 'id:list'))) {
                        frm.elements[i].checked = false;
                    }
                }
                isSelected = false;
            }
        }
    };
}

if (fCheckSelection == undefined) {
    var fCheckSelection = function(){
        var frm = document.frmAllocateKeywords;
        if(frm == undefined){
            var frm = document.objectItems;
        }

        if(frm != undefined){
            var i;
            check = false;

            for(i=0; i<frm.elements.length; i++){
                if (frm.elements[i].type == "checkbox" && ((frm.elements[i].name == 'checked_paths:list') || (frm.elements[i].name == 'id:list'))) {
                    check = true; break;
                }
            }

            return check;
        }
    };
}


function fAllocateKeywords() {
    if (fCheckSelection()) {
	document.objectItems.action="allocate_keywords_html";
	document.objectItems.submit();
    }else {
	alert('Please select on or more items for which you want to allocate keywords');
    }
}
