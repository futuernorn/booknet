<?php
/**
* @link http://gist.github.com/385876
*/
$ddl = csv_to_array("input.csv");
$currentTable = "";
foreach ($ddl as $attribute) {
  if ($currentTable != $attribute['table_name']) {
    if ($currentTable != "")
      echo ");</br></br>";
    $currentTable = $attribute['table_name'];
    echo "CREATE TABLE $currentTable(";
    echo "</br>";  
  }
  $attributeName = $attribute['Attribute'];
  $dataType = $attribute['sql_type'];
  $isKey = " ";
  if ($dataType == 'varchar')
    $dataType = "varchar(50)";
  if ($attribute['Key Type'] == "Primary")
    $isKey = " Primary Key";
  echo "\t$attributeName \t\t$dataType$isKey\t\tNOT NULL,";
  echo "</br>";
}
echo ");";
echo "</br>";

// echo "<pre>";
// print_r($ddl);
// echo "</pre>";

function csv_to_array($filename='', $delimiter=',')
{
    if(!file_exists($filename) || !is_readable($filename))
        return FALSE;

    $header = NULL;
    $data = array();
    if (($handle = fopen($filename, 'r')) !== FALSE)
    {
        while (($row = fgetcsv($handle, 1000, $delimiter)) !== FALSE)
        {
            if(!$header)
                $header = $row;
            else
                $data[] = array_combine($header, $row);
        }
        fclose($handle);
    }
    return $data;
}

?>