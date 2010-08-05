function process_table()
{
	multiply('total_requested_t1', 'requested_t1_hours', 'requested_t1_euro');
	multiply('total_requested_t2', 'requested_t2_hours', 'requested_t2_euro');
	multiply('total_requested_t3', 'requested_t3_hours', 'requested_t3_euro');
	sum('total_requested_labor', 'total_requested_t1', 'total_requested_t2', 'total_requested_t3');
	sum('total_requested_material_other', 'requested_material_costs', 'requested_other_costs');
	sum('total_requested', 'total_requested_labor', 'total_requested_material_other');
	multiply('total_own_t1', 'own_t1_hours', 'own_t1_euro');
	multiply('total_own_t2', 'own_t2_hours', 'own_t2_euro');
	multiply('total_own_t3', 'own_t3_hours', 'own_t3_euro');
	sum('total_own_labor', 'total_own_t1', 'total_own_t2', 'total_own_t3');
	sum('total_own_material_other', 'own_material_costs', 'own_other_costs');
	sum('total_own', 'total_own_labor', 'total_own_material_other');
}
function sum()
{
	var arguments = sum.arguments;
	document.getElementById(arguments[0]).value = 0;
	for (var i = 1; i < arguments.length; i++)
	{
		if (document.getElementById(arguments[i]).value == '' )
		{
			document.getElementById(arguments[i]).value = 0;
		}
		document.getElementById(arguments[0]).value = parseFloat(document.getElementById(arguments[0]).value) + parseFloat(document.getElementById(arguments[i]).value);
	}
}
function multiply()
{
	var arguments = multiply.arguments;
	document.getElementById(arguments[0]).value = 1;
	for (var i = 1; i < arguments.length; i++)
	{
		if (document.getElementById(arguments[i]).value == '' )
		{
			document.getElementById(arguments[i]).value = 0;
		}
		document.getElementById(arguments[0]).value = parseFloat(document.getElementById(arguments[0]).value) * parseFloat(document.getElementById(arguments[i]).value);
	}
}
$(document).ready(function() {
   process_table();
   });
