<?php

/**
 * 發送 GET 請求
 *
 * @param string $url 目標 URL
 * @param array $headers 自定義 HTTP 請求頭部
 * @param string $cacert_path 根證書的路徑（如果遇到 SSL 問題，可以設置）
 * @return mixed|false 返回響應正文，或在錯誤時返回 false
 */
function send_get_request($url, $headers = [], $cacert_path = null) {
    // 初始化 cURL
    $ch = curl_init();
    
    // 設定 cURL 選項
    curl_setopt($ch, CURLOPT_URL, $url);              // 設定請求 URL
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);    // 返回響應，而不是直接輸出
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);    // 允許重定向

    // 如果提供了自定義的 HTTP 請求頭部
    if (!empty($headers)) {
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    }

    // 如果指定了根證書文件，設置 cURL 以支持 SSL 驗證
    if ($cacert_path !== null) {
        curl_setopt($ch, CURLOPT_CAINFO, $cacert_path); // 設置根證書路徑
    }else{
        // 禁用 SSL 憑證驗證（不推薦使用，僅用於測試）
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    }

    // 執行請求並獲取響應
    $response = curl_exec($ch);

    // 檢查是否有錯誤
    if (curl_errno($ch)) {
        echo 'cURL Error: ' . curl_error($ch);
        $response = false;
    }

    // 關閉 cURL 連接
    curl_close($ch);

    if ($response === false) {
        return "Error: " . curl_error($ch);
    } else {
        // 嘗試解析 JSON 響應
        return json_decode($response, true);  // 轉換為關聯數組
    }
}


function url($url, $params = []) {
    /*
    $params = [
        'location' => '23.566429, 120.472377',  // 搜尋中心點，格式：latitude,longitude
        'radius' => '1000',                     // 搜尋範圍的半徑，以meter為單位  {1 ~ 50,000}
        'keyword' => '午餐',                    // 搜尋關鍵字，支持中文，若直接在網址需使用 urlencode()
        'type' => 'restaurant',                 // 地點類型（如 restaurant, park, gym 等）
        'opennow' => 'false',                   // 是否只返回當前開放的地點 {true | false}
        'minprice' => '0',                      // 最低價格級別，僅適用於某些類型 {0 ~ 4}
        'maxprice' => '4',                      // 最高價格級別，僅適用於某些類型 {0 ~ 4}
        'rankby' => 'prominence',               // 結果排序方式 {prominence(知名度) | distance}
        'language' => 'zh-TW',                  // 返回結果的語言 {en | zh-TW | etc.}
        'key' => '<Your API Key>'               // Google Maps API 的 API Key
    ];
    pagetoken:	CkQ2AAAA...             // 用於分頁查詢的 next_page_token（從上一頁結果中獲取）	
    fields:		name,vicinity,geometry  // 限制返回的字段，減少不必要的數據
    */
    $query_string = http_build_query($params);
    return $url . '?' . $query_string;
    // return $url . "&language=zh-TW&key=AIzaSyAuPZ4LWUaWTFxWGgl09CxRlze6Diq3dZE";
}

$api_key = 'AIzaSyAuPZ4LWUaWTFxWGgl09CxRlze6Diq3dZE';
$params = [
    'location' => '23.566429, 120.472377', // 25.0338,121.5646
    'radius' => '1000',
    'keyword' => '午餐',
    'type' => 'restaurant',
    'opennow' => 'false',
    'minprice' => '0',
    'maxprice' => '4',
    'rankby' => 'prominence',
    'language' => 'zh-TW',
    'key' => 'AIzaSyAuPZ4LWUaWTFxWGgl09CxRlze6Diq3dZE'
];

$place_detail_params = [
    'placeid' => 'ChIJUVWFEyGUbjQRvMIXG_6EvsA',
    'key' => 'AIzaSyAuPZ4LWUaWTFxWGgl09CxRlze6Diq3dZE'
];
$url = url("https://maps.googleapis.com/maps/api/place/nearbysearch/json", $params);
$place_detail = url("https://maps.googleapis.com/maps/api/place/details/json", ['placeid' => 'ChIJUVWFEyGUbjQRvMIXG_6EvsA', 'key' => $api_key]);
echo $url;
// $response = send_get_request($place_detail);
// print_r($response["result"]['current_opening_hours']['weekday_text']); // ['results']

// if ($response !== false) {
//     $results = $response['results'];
//     for ($i = 0; $i < count($results); $i++) {
//         // 顯示每個結果（你可以根據需要進行處理）
//         echo "Place " . ($i + 1) . ":\n";
//         echo "ID: " . $results[$i]['place_id'] . "\n";
//         echo "Name: " . $results[$i]['name'] . "\n";
//         echo "lat: " . $results[$i]['geometry']['location']['lat'] . "\n";
//         echo "lng: " . $results[$i]['geometry']['location']['lng'] . "\n";
//         // echo "Address: " . $results[$i]['vicinity'] . "\n";
//         echo "--------------------\n";
//     }
// } else {
//     echo "Request failed.";
// }



// 获取网页内容
$html = file_get_contents('https://www.google.com.tw/maps/place/%E9%98%BF%E5%BF%A0%E6%B5%B7%E7%94%A2%E7%BE%8A%E8%82%89/@23.5258144,120.4391563,17z/data=!3m1!4b1!4m6!3m5!1s0x346e95fe84648d7f:0x1ed10e323282eaff!8m2!3d23.5258144!4d120.4391563!16s%2Fg%2F11dxdpc5v8?entry=ttu&g_ep=EgoyMDI0MTExMi4wIKXMDSoASAFQAw%3D%3D');
$dom = new DOMDocument();
libxml_use_internal_errors(true);  // 关闭 HTML 解析错误警告
$dom->loadHTML($html);
libxml_clear_errors();

// 创建 XPath 对象
$xpath = new DOMXPath($dom);
echo $html;
// 查找所有 <a> 标签的 href 属性
$links = $xpath->query('//div[@class="zSdcRe"]');
echo $links->item(0)->nodeValue;

foreach ($links as $link) {
    echo "--------------------\n";
    echo $link->nodeValue . "\n";
}
?>

<!-- 

評論的部分，試著幫我抓最近5個好評跟差評的文字內容 

-->