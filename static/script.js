$(document).ready(function() {
	function validate(){
		var max = parseInt(document.getElementById('endYear').value);
		var min = parseInt(document.getElementById('startYear').value);
		if(min > max){
			alert('Year range should be positive, enter as (Start Year --> End Year)');
		return false;
		}
		else {
		}
	}
}