<?php
/**
 * Plugin Name: Move In Thailand Experience
 * Description: Editorial website, native page drafts and a private enquiry desk.
 * Version: 1.0.0
 */
defined('ABSPATH') || exit;
define('MIT_EXPERIENCE_VERSION', '1.0.0');
function mit_text_length($value) { return function_exists('mb_strlen') ? mb_strlen($value) : strlen($value); }
function mit_text_slice($value,$length) { return function_exists('mb_substr') ? mb_substr($value,0,$length) : substr($value,0,$length); }

function mit_site_directory() { return WP_CONTENT_DIR . '/mit-site'; }
function mit_manifest() {
    static $manifest = null;
    if ($manifest === null) {
        $file = mit_site_directory() . '/routes.json';
        $manifest = is_readable($file) ? json_decode(file_get_contents($file), true) : array();
        if (!is_array($manifest) || ($manifest['domain'] ?? '') !== 'moveinthailand.com') { $manifest = array(); }
    }
    return $manifest;
}
function mit_route($path) {
    $normal = '/' . trim($path, '/') . '/';
    if ($normal === '//') { $normal = '/'; }
    foreach (mit_manifest()['routes'] ?? array() as $route) { if ($route['path'] === $normal) { return $route; } }
    return null;
}
function mit_page_file($route) {
    $root = realpath(mit_site_directory());
    $file = realpath(mit_site_directory() . '/' . $route['file']);
    return $root && $file && strpos($file, $root . DIRECTORY_SEPARATOR) === 0 && is_readable($file) ? $file : false;
}
function mit_serve_sitemap() {
    $path=parse_url($_SERVER['REQUEST_URI'] ?? '/',PHP_URL_PATH);
    if($path!=='/mit-sitemap.xml'){return;}
    $manifest=mit_manifest();$routes=$manifest['routes']??array();if(!$routes){return;}
    $dates=array();foreach(get_posts(array('post_type'=>'mit_page','post_status'=>'publish','numberposts'=>1000,'suppress_filters'=>true)) as $page){$dates[get_post_meta($page->ID,'_mit_route',true)]=$page->post_modified_gmt;}
    status_header(200);header('Content-Type: application/xml; charset=UTF-8');
    echo '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">';
    foreach($routes as $route){$stamp=isset($dates[$route['path']])?gmdate('c',strtotime($dates[$route['path']].' UTC')):($manifest['built_at'].'T00:00:00Z');echo '<url><loc>'.htmlspecialchars(home_url($route['path']),ENT_XML1|ENT_COMPAT,'UTF-8').'</loc><lastmod>'.esc_html($stamp).'</lastmod></url>';}
    echo '</urlset>';exit;
}
// Existing SEO plugins may claim *-sitemap.xml during parse_request.
add_action('init','mit_serve_sitemap',1);
function mit_register_types() {
    register_post_type('mit_page', array(
        'labels' => array('name'=>'Move In Thailand Pages','singular_name'=>'Move In Thailand Page','edit_item'=>'Edit website page','add_new_item'=>'Add website page draft'),
        'public'=>false,'show_ui'=>true,'show_in_menu'=>true,'show_in_rest'=>true,'rest_base'=>'mit-pages','menu_icon'=>'dashicons-admin-site-alt3','menu_position'=>21,
        'supports'=>array('title','editor','revisions','author'),'capability_type'=>'page','map_meta_cap'=>true,'capabilities'=>array('create_posts'=>'do_not_allow'),
    ));
    register_post_type('mit_enquiry', array(
        'labels'=>array('name'=>'Move Enquiries','singular_name'=>'Move Enquiry','edit_item'=>'Review move enquiry'),
        'public'=>false,'show_ui'=>true,'show_in_rest'=>false,'show_in_menu'=>true,'menu_icon'=>'dashicons-email-alt','menu_position'=>22,
        'supports'=>array('title'),'capabilities'=>array('edit_post'=>'manage_options','read_post'=>'manage_options','delete_post'=>'manage_options','edit_posts'=>'manage_options','edit_others_posts'=>'manage_options','publish_posts'=>'manage_options','read_private_posts'=>'manage_options','delete_posts'=>'manage_options','delete_others_posts'=>'manage_options','delete_private_posts'=>'manage_options','delete_published_posts'=>'manage_options','edit_private_posts'=>'manage_options','edit_published_posts'=>'manage_options','create_posts'=>'do_not_allow'),
        'map_meta_cap'=>false,
    ));
}
add_action('init', 'mit_register_types', 10);

/* Apply bundled defaults only while a page still matches its last seeded copy. */
function mit_seed_editorial_pages() {
    $manifest=mit_manifest();$routes=$manifest['routes']??array();
    $version=$manifest['content_version']??($manifest['version']??'');
    if ($version && get_option('mit_editorial_content_version') === $version) { return; }
    if (!$routes) { return; }
    $lock = get_option('mit_editorial_seed_lock');
    if ($lock && (int)$lock > time() - 120) { return; }
    if ($lock) { delete_option('mit_editorial_seed_lock'); }
    if (!add_option('mit_editorial_seed_lock', time(), '', false)) { return; }
    $completed = true;
    kses_remove_filters();
    foreach ($routes as $route) {
        $existing = get_posts(array('post_type'=>'mit_page','post_status'=>'any','numberposts'=>1,'meta_key'=>'_mit_route','meta_value'=>$route['path'],'suppress_filters'=>true));
        $file = mit_page_file($route);
        if (!$file) { $completed=false; continue; }
        $html = file_get_contents($file);
        if (!preg_match('/<!--mit-content-start-->(.*?)<!--mit-content-end-->/s', $html, $match)) { $completed=false; continue; }
        $default='<!-- wp:html -->'.$match[1].'<!-- /wp:html -->';$hash=hash('sha256',$default);
        if($existing){
            $page=$existing[0];$old_hash=get_post_meta($page->ID,'_mit_seed_hash',true);$current_hash=hash('sha256',$page->post_content);
            if(!$old_hash){$old_hash=$hash;}
            if($current_hash===$old_hash){
                if($current_hash!==$hash){$updated=wp_update_post(array('ID'=>$page->ID,'post_content'=>wp_slash($default)),true);if(is_wp_error($updated)){$completed=false;continue;}}
                foreach(array('title','description') as $field){$meta='_mit_seo_'.$field;$previous=get_post_meta($page->ID,'_mit_seed_'.$field,true);$current=get_post_meta($page->ID,$meta,true);if(!$previous){$previous=$route[$field];}if($current===$previous){update_post_meta($page->ID,$meta,$route[$field]);}update_post_meta($page->ID,'_mit_seed_'.$field,$route[$field]);}
                update_post_meta($page->ID,'_mit_seed_hash',$hash);update_post_meta($page->ID,'_mit_source_update_pending','0');
            }else{
                update_post_meta($page->ID,'_mit_source_update_pending',$hash!==$old_hash?'1':'0');
                if(!get_post_meta($page->ID,'_mit_seed_hash',true)){update_post_meta($page->ID,'_mit_seed_hash',$hash);}
            }
            continue;
        }
        $id = wp_insert_post(array('post_type'=>'mit_page','post_status'=>'publish','post_title'=>wp_strip_all_tags($route['title']),'post_content'=>wp_slash($default),'meta_input'=>array('_mit_route'=>$route['path'],'_mit_seo_title'=>$route['title'],'_mit_seo_description'=>$route['description'],'_mit_seed_hash'=>$hash,'_mit_seed_title'=>$route['title'],'_mit_seed_description'=>$route['description'])), true);
        if (is_wp_error($id) || !$id) { $completed=false; }
    }
    kses_init_filters();
    if ($completed) { update_option('mit_editorial_seeded','1',false);update_option('mit_editorial_content_version',$version,false); }
    delete_option('mit_editorial_seed_lock');
}
add_action('init','mit_seed_editorial_pages',30);

function mit_published_page($path) {
    $pages=get_posts(array('post_type'=>'mit_page','post_status'=>'publish','numberposts'=>1,'meta_key'=>'_mit_route','meta_value'=>$path,'suppress_filters'=>true));
    return $pages ? $pages[0] : null;
}

function mit_render_site() {
    if (is_admin() || wp_doing_ajax() || (defined('REST_REQUEST') && REST_REQUEST) || is_feed()) { return; }
    $path=rawurldecode(parse_url($_SERVER['REQUEST_URI'] ?? '/',PHP_URL_PATH) ?: '/');
    if ($path === '/mit-sitemap.xml') {
        $file=mit_site_directory().'/sitemap.xml';
        if (is_readable($file)) { status_header(200);header('Content-Type: application/xml; charset=UTF-8');readfile($file);exit; }
    }
    $normal='/' . trim($path,'/') . '/'; if ($normal==='//') { $normal='/'; }
    $manifest=mit_manifest();
    if (isset($manifest['aliases'][$normal])) { wp_safe_redirect(home_url($manifest['aliases'][$normal]),301);exit; }
    $route=mit_route($normal);
    if (!$route) { return; }
    $file=mit_page_file($route);if (!$file) { return; }
    $page=mit_published_page($route['path']);
    $preview_id=absint($_GET['mit_preview'] ?? 0);
    $preview=false;
    if ($preview_id && current_user_can('edit_post',$preview_id) && wp_verify_nonce(sanitize_text_field(wp_unslash($_GET['_mit_nonce'] ?? '')), 'mit_preview_'.$preview_id)) {
        $candidate=get_post($preview_id);
        if ($candidate && $candidate->post_type==='mit_page' && get_post_meta($candidate->ID,'_mit_route',true)===$route['path']) { $page=$candidate;$preview=true; }
    }
    $html=file_get_contents($file);
    if ($page && trim($page->post_content)!=='') {
        $content=do_blocks($page->post_content);
        $html=preg_replace_callback('/<!--mit-content-start-->.*?<!--mit-content-end-->/s',function() use($content){return '<!--mit-content-start-->'.$content.'<!--mit-content-end-->';},$html,1);
        $seo_title=get_post_meta($page->ID,'_mit_seo_title',true);
        $description=get_post_meta($page->ID,'_mit_seo_description',true);
        if ($seo_title) {
            $html=preg_replace_callback('/<title>.*?<\/title>/s',function() use($seo_title){return '<title>'.esc_html($seo_title).'</title>';},$html,1);
            $html=preg_replace_callback('/(<meta property="og:title" content=")[^"]*(">)/',function($m) use($seo_title){return $m[1].esc_attr($seo_title).$m[2];},$html);
        }
        if ($description) {
            $html=preg_replace_callback('/(<meta (?:name="description"|property="og:description") content=")[^"]*(">)/',function($m) use($description){return $m[1].esc_attr($description).$m[2];},$html);
        }
        $html=preg_replace_callback('/<script type="application\/ld\+json">(.*?)<\/script>/s',function($m) use($seo_title,$description,$content){
            $data=json_decode($m[1],true);
            if (!is_array($data)) { return ''; }
            // Build FAQ data from the currently published answers, including staff edits.
            $data['@graph']=array_values(array_filter($data['@graph'] ?? array(),function($item){return ($item['@type'] ?? '')!=='FAQPage';}));
            foreach ($data['@graph'] as &$item) { if (($item['@type'] ?? '')==='WebPage') { if ($seo_title) {$item['name']=$seo_title;} if ($description) {$item['description']=$description;} } } unset($item);
            if(preg_match_all('/<details>\s*<summary>(.*?)<\/summary>\s*<p>(.*?)<\/p>\s*<\/details>/s',$content,$faq_matches,PREG_SET_ORDER)){
                $questions=array();
                foreach($faq_matches as $faq){$question=preg_replace('/<span\b[^>]*>.*?<\/span>/s','',$faq[1]);$questions[]=array('@type'=>'Question','name'=>trim(html_entity_decode(wp_strip_all_tags($question),ENT_QUOTES|ENT_HTML5,'UTF-8')),'acceptedAnswer'=>array('@type'=>'Answer','text'=>trim(html_entity_decode(wp_strip_all_tags($faq[2]),ENT_QUOTES|ENT_HTML5,'UTF-8'))));}
                $data['@graph'][]=array('@type'=>'FAQPage','mainEntity'=>$questions);
            }
            return '<script type="application/ld+json">'.wp_json_encode($data,JSON_HEX_TAG|JSON_HEX_AMP|JSON_HEX_APOS|JSON_HEX_QUOT).'</script>';
        },$html,1);
    }
    $settings=get_option('mit_site_settings',array());
    $html=preg_replace_callback('/<script id="mit-config" type="application\/json">(.*?)<\/script>/s',function($m) use($settings,$preview){
        $config=json_decode($m[1],true) ?: array();
        $config['apiBase']=rest_url('mit/v1/');$config['preview']=$preview;
        $config['whatsapp']=$settings['whatsapp'] ?? '';$config['fees']=$settings['fees'] ?? array();
        return '<script id="mit-config" type="application/json">'.wp_json_encode($config,JSON_HEX_TAG|JSON_HEX_AMP|JSON_HEX_APOS|JSON_HEX_QUOT).'</script>';
    },$html,1);
    if ($preview) {
        $html=str_replace('<meta name="robots" content="index,follow">','<meta name="robots" content="noindex,nofollow">',$html);
        $html=preg_replace('/(<body[^>]*>)/','$1<div class="mit-preview-banner">Website draft preview. Publish the page in WordPress to make changes live.</div>',$html,1);
        nocache_headers();
    }
    status_header(200);header('Content-Type: text/html; charset=UTF-8');
    header('X-Content-Type-Options: nosniff');header('Referrer-Policy: strict-origin-when-cross-origin');
    echo $html;exit;
}
add_action('template_redirect','mit_render_site',0);
add_filter('robots_txt',function($text){return rtrim($text)."\nSitemap: ".home_url('/mit-sitemap.xml')."\n";},99);
// Add our routes through the existing SEO plugin's documented index hook.
add_filter('aioseo_sitemap_indexes',function($indexes){
    $manifest=mit_manifest();if(empty($manifest['routes'])){return $indexes;}
    $url=home_url('/mit-sitemap.xml');foreach($indexes as $index){if(($index['loc']??'')===$url){return $indexes;}}
    $latest=get_posts(array('post_type'=>'mit_page','post_status'=>'publish','numberposts'=>1,'orderby'=>'modified','order'=>'DESC','suppress_filters'=>true));
    $stamp=$latest?gmdate('c',strtotime($latest[0]->post_modified_gmt.' UTC')):($manifest['built_at'].'T00:00:00Z');
    $indexes[]=array('loc'=>$url,'lastmod'=>$stamp,'count'=>count($manifest['routes']));return $indexes;
});

/* Native WordPress drafts, revisions, publishing and scoped staff permissions. */
add_filter('preview_post_link',function($link,$post){
    if ($post->post_type!=='mit_page') { return $link; }
    $route=get_post_meta($post->ID,'_mit_route',true);
    return $route ? add_query_arg(array('mit_preview'=>$post->ID,'_mit_nonce'=>wp_create_nonce('mit_preview_'.$post->ID)),home_url($route)) : $link;
},10,2);
add_filter('post_type_link',function($link,$post){$route=$post->post_type==='mit_page'?get_post_meta($post->ID,'_mit_route',true):'';return $route?home_url($route):$link;},10,2);
add_action('add_meta_boxes',function(){
    add_meta_box('mit-page-details','Website route & search description','mit_page_details_box','mit_page','side');
    add_meta_box('mit-enquiry-details','Enquiry & follow-up','mit_enquiry_details_box','mit_enquiry','normal','high');
});
function mit_page_details_box($post) {
    wp_nonce_field('mit_page_meta','mit_page_meta_nonce');
    $route=get_post_meta($post->ID,'_mit_route',true);
    echo '<p><strong>Website address</strong><br>'.esc_html(home_url($route?:'/')).'</p>';
    echo '<p>Edit the HTML block to change the page. Save a draft or revision, preview, then publish. The navigation and footer are shared.</p>';
    if(get_post_meta($post->ID,'_mit_source_update_pending',true)==='1'){echo '<p><strong>A newer default copy exists in GitHub. Your published edits were kept; ask the site maintainer to review the copy before replacing it.</strong></p>';}
    echo '<p><label>Search title<input name="mit_seo_title" class="widefat" maxlength="180" value="'.esc_attr(get_post_meta($post->ID,'_mit_seo_title',true)).'"></label></p>';
    echo '<p><label>Search description<textarea name="mit_seo_description" class="widefat" rows="4" maxlength="320">'.esc_textarea(get_post_meta($post->ID,'_mit_seo_description',true)).'</textarea></label></p>';
    if ($route) { echo '<p><a href="'.esc_url(home_url($route)).'" target="_blank" rel="noopener">View published page</a></p>'; }
}
add_action('save_post_mit_page',function($id){
    if (wp_is_post_revision($id) || (defined('DOING_AUTOSAVE') && DOING_AUTOSAVE) || !current_user_can('edit_post',$id)) { return; }
    if (!wp_verify_nonce(sanitize_text_field(wp_unslash($_POST['mit_page_meta_nonce'] ?? '')),'mit_page_meta')) { return; }
    update_post_meta($id,'_mit_seo_title',sanitize_text_field(wp_unslash($_POST['mit_seo_title'] ?? '')));
    update_post_meta($id,'_mit_seo_description',sanitize_textarea_field(wp_unslash($_POST['mit_seo_description'] ?? '')));
});

function mit_enquiry_details_box($post) {
    if (!current_user_can('manage_options')) { return; }
    $data=get_post_meta($post->ID,'_mit_enquiry',true);if (!is_array($data)) {return;}
    wp_nonce_field('mit_enquiry_meta','mit_enquiry_meta_nonce');
    echo '<table class="widefat striped"><tbody>';
    foreach (array('reference'=>'Reference','name'=>'Name','email'=>'Email','phone'=>'Phone / messaging','interest'=>'Interest','timeline'=>'Timeline','budget'=>'Monthly budget (THB)','message'=>'Message','source'=>'Enquiry source','submitted_at'=>'Submitted (UTC)','contact_consent'=>'Enquiry contact permission','marketing_consent'=>'Optional marketing permission','consent_version'=>'Privacy version') as $key=>$label) {
        $value=$data[$key] ?? '';if (is_bool($value)) {$value=$value?'Yes':'No';}
        echo '<tr><th style="width:210px">'.esc_html($label).'</th><td style="white-space:pre-wrap">'.esc_html((string)$value).'</td></tr>';
    }
    echo '</tbody></table><p><label>Follow-up status <select name="mit_lead_status">';
    $state=get_post_meta($post->ID,'_mit_lead_status',true) ?: 'new';
    foreach (array('new'=>'New','contacted'=>'Contacted','active'=>'Ongoing requested service','closed'=>'Closed') as $value=>$label) {echo '<option value="'.esc_attr($value).'" '.selected($state,$value,false).'>'.esc_html($label).'</option>';}
    echo '</select></label></p><p>Keep only the information needed for this enquiry. Initial enquiries are moved to WordPress Trash after 180 days unless marked as an ongoing requested service. A legal hold also needs to be recorded in the follow-up notes.</p>';
    echo '<p><label>Follow-up notes<textarea class="widefat" rows="5" name="mit_lead_notes">'.esc_textarea(get_post_meta($post->ID,'_mit_lead_notes',true)).'</textarea></label></p>';
    echo '<p><label><input type="checkbox" name="mit_legal_hold" value="1" '.checked(get_post_meta($post->ID,'_mit_legal_hold',true),'1',false).'> Retain for a documented legal obligation</label></p>';
    if (get_post_meta($post->ID,'_mit_notification',true)==='failed') {echo '<p><strong>Email notification was not accepted by WordPress. The enquiry is saved here.</strong></p>';}
}
add_action('save_post_mit_enquiry',function($id){
    if (!current_user_can('manage_options') || wp_is_post_revision($id) || !wp_verify_nonce(sanitize_text_field(wp_unslash($_POST['mit_enquiry_meta_nonce'] ?? '')),'mit_enquiry_meta')) {return;}
    $state=sanitize_key($_POST['mit_lead_status'] ?? 'new');
    if (in_array($state,array('new','contacted','active','closed'),true)) {update_post_meta($id,'_mit_lead_status',$state);}
    update_post_meta($id,'_mit_lead_notes',sanitize_textarea_field(wp_unslash($_POST['mit_lead_notes'] ?? '')));
    update_post_meta($id,'_mit_legal_hold',isset($_POST['mit_legal_hold'])?'1':'0');
});
add_filter('manage_mit_enquiry_posts_columns',function($columns){return array('cb'=>$columns['cb'],'title'=>'Enquiry','mit_interest'=>'Interest','mit_timeline'=>'Timeline','mit_status'=>'Follow-up','date'=>'Received');});
add_action('manage_mit_enquiry_posts_custom_column',function($column,$id){$data=get_post_meta($id,'_mit_enquiry',true);if($column==='mit_interest'){echo esc_html($data['interest']??'');}if($column==='mit_timeline'){echo esc_html($data['timeline']??'');}if($column==='mit_status'){echo esc_html(get_post_meta($id,'_mit_lead_status',true)?:'new');}},10,2);
add_filter('manage_mit_page_posts_columns',function($columns){$columns['mit_route']='Website address';return $columns;});
add_action('manage_mit_page_posts_custom_column',function($column,$id){if($column==='mit_route'){echo esc_html(get_post_meta($id,'_mit_route',true));}},10,2);

/* Only administrators can change delivery settings or see private leads. */
add_action('admin_menu',function(){add_options_page('Move In Thailand Settings','Move In Thailand','manage_options','mit-settings','mit_settings_screen');});
add_action('admin_init',function(){register_setting('mit_settings','mit_site_settings',array('sanitize_callback'=>'mit_sanitize_settings','default'=>array()));});
function mit_sanitize_settings($input) {
    $output=array();
    $output['whatsapp']=preg_replace('/\D/','',(string)($input['whatsapp']??''));
    if ($output['whatsapp'] && !preg_match('/^\d{7,15}$/',$output['whatsapp'])) {$output['whatsapp']='';add_settings_error('mit_site_settings','mit_whatsapp','Use a full international number with country code.');}
    $output['notification_email']=sanitize_email($input['notification_email']??'');
    $output['notifications']=!empty($input['notifications']);
    $output['fees']=array();foreach(array('visa','landing','care','business') as $key){$output['fees'][$key]=mit_text_slice(sanitize_text_field($input['fees'][$key]??''),100);}
    return $output;
}
function mit_settings_screen() {
    if(!current_user_can('manage_options')){return;}$options=get_option('mit_site_settings',array());
    echo '<div class="wrap"><h1>Move In Thailand</h1><p>Page copy: <a href="'.esc_url(admin_url('edit.php?post_type=mit_page')).'">Move In Thailand Pages</a>. Enquiries: <a href="'.esc_url(admin_url('edit.php?post_type=mit_enquiry')).'">Move Enquiries</a>.</p><form action="options.php" method="post">';settings_fields('mit_settings');
    echo '<table class="form-table"><tr><th>Public WhatsApp number</th><td><input name="mit_site_settings[whatsapp]" value="'.esc_attr($options['whatsapp']??'').'" class="regular-text"><p class="description">Optional. Include the country code. Leave blank to keep the WhatsApp link hidden.</p></td></tr>';
    echo '<tr><th>Enquiry notifications</th><td><label><input type="checkbox" name="mit_site_settings[notifications]" value="1" '.checked($options['notifications']??true,true,false).'> Notify the configured inbox when an enquiry is saved</label></td></tr>';
    echo '<tr><th>Notification inbox</th><td><input type="email" name="mit_site_settings[notification_email]" value="'.esc_attr($options['notification_email']??'').'" class="regular-text"><p class="description">Leave blank to use the existing WordPress administrative inbox. This address is never published on the website. Saving enquiries does not depend on successful email delivery.</p></td></tr>';
    foreach(array('visa'=>'Visa coordination','landing'=>'Arrival support','care'=>'Residency Care','business'=>'Business coordination') as $key=>$label){echo '<tr><th>'.esc_html($label).' fee label</th><td><input name="mit_site_settings[fees]['.esc_attr($key).']" value="'.esc_attr($options['fees'][$key]??'').'" class="regular-text"><p class="description">Optional confirmed service price, with currency and scope. Blank displays “Written quote”.</p></td></tr>';}
    echo '</table>';submit_button();echo '</form><h2>Restore the original website</h2><p>In cPanel File Manager, rename <code>wp-content/mu-plugins/mit-experience.php</code> to <code>mit-experience.php.disabled</code>. The previous WordPress pages and theme remain in place. Website page drafts and enquiries remain stored in WordPress.</p></div>';
}

/* Public form: signed bootstrap, same-origin check, limits and durable consent. */
function mit_form_token() {
    $body=(time()+1200).'.'.wp_generate_password(18,false,false);
    return $body.'.'.hash_hmac('sha256',$body,wp_salt('nonce'));
}
function mit_token_valid($token) {
    $parts=explode('.',(string)$token);
    if(count($parts)!==3 || !ctype_digit($parts[0]) || (int)$parts[0]<time() || (int)$parts[0]>time()+1800){return false;}
    return hash_equals(hash_hmac('sha256',$parts[0].'.'.$parts[1],wp_salt('nonce')),$parts[2]);
}
function mit_same_origin($request) {
    $origin=$request->get_header('origin');if(!$origin){return true;}
    $allowed=wp_parse_url(home_url());$incoming=wp_parse_url($origin);
    return $incoming && strtolower($incoming['host']??'')===strtolower($allowed['host']??'') && strtolower($incoming['scheme']??'')===strtolower($allowed['scheme']??'');
}
add_action('rest_api_init',function(){
    register_rest_route('mit/v1','/bootstrap',array('methods'=>'GET','permission_callback'=>'__return_true','callback'=>function($request){
        if(!mit_same_origin($request)){return new WP_Error('mit_origin','Reload the form on the Move In Thailand website.',array('status'=>403));}
        $response=new WP_REST_Response(array('token'=>mit_form_token(),'expires_in'=>1200),200);$response->header('Cache-Control','no-store, private');return $response;
    }));
    register_rest_route('mit/v1','/enquiries',array('methods'=>'POST','permission_callback'=>'__return_true','callback'=>'mit_save_enquiry'));
});
function mit_save_enquiry($request) {
    if(!mit_same_origin($request)){return new WP_Error('mit_origin','Please use the form on the Move In Thailand website.',array('status'=>403));}
    if(strlen($request->get_body())>20000){return new WP_Error('mit_size','Please shorten your message and try again.',array('status'=>413));}
    $data=$request->get_json_params();if(!is_array($data)){$data=array();}
    foreach($data as $value){if(is_array($value)||is_object($value)){return new WP_Error('mit_fields','Please check the form fields.',array('status'=>400));}}
    if(!mit_token_valid($data['token']??'')){return new WP_Error('mit_token','Your form session expired. Please try again.',array('status'=>403));}
    if(!empty($data['website'])){return new WP_Error('mit_spam','The enquiry could not be accepted. Please reload the form.',array('status'=>400));}
    $name=trim(sanitize_text_field($data['name']??''));$email=sanitize_email($data['email']??'');
    $interest=sanitize_key($data['interest']??'');$timeline=sanitize_key($data['timeline']??'');
    $interests=array('visa','dtv','retirement','ltr','thailand-privilege','marriage','education','homes','business','care','budget','fees','privacy','other');
    $timelines=array('soon','later','year','exploring','already');
    if(!$name || mit_text_length($name)>120 || !is_email($email) || strlen($email)>200 || !in_array($interest,$interests,true) || !in_array($timeline,$timelines,true) || ($data['consent']??false)!==true){
        return new WP_Error('mit_fields','Please add your name, email, interest, timeline and permission to answer your enquiry.',array('status'=>400));
    }
    $phone=sanitize_text_field($data['phone']??'');$message=sanitize_textarea_field($data['message']??'');
    if(mit_text_length($phone)>40 || mit_text_length($message)>3000){return new WP_Error('mit_length','Please shorten the phone number or message.',array('status'=>400));}
    $budget=$data['budget']??'';
    if($budget!=='' && (!is_numeric($budget)||(float)$budget<0||(float)$budget>10000000)){return new WP_Error('mit_budget','Use a non-negative monthly budget, or leave it blank.',array('status'=>400));}
    $request_id=sanitize_text_field($data['request_id']??'');
    if(!preg_match('/^[a-zA-Z0-9-]{10,80}$/',$request_id)){return new WP_Error('mit_request','Please reload the form and try again.',array('status'=>400));}
    $request_hash=hash_hmac('sha256',$request_id.'|'.$email,wp_salt('auth'));
    $existing=get_posts(array('post_type'=>'mit_enquiry','post_status'=>'private','numberposts'=>1,'meta_key'=>'_mit_request_hash','meta_value'=>$request_hash,'suppress_filters'=>true));
    if($existing){$saved=get_post_meta($existing[0]->ID,'_mit_enquiry',true);return new WP_REST_Response(array('saved'=>true,'reference'=>$saved['reference']),200);}
    $network=hash_hmac('sha256',($_SERVER['REMOTE_ADDR']??'unknown').'|'.gmdate('Y-m-d-H'),wp_salt('auth'));
    $limit_key='mit_rate_'.substr($network,0,32);$count=(int)get_transient($limit_key);
    if($count>=10){return new WP_Error('mit_limit','Too many enquiries from this connection. Please try again later.',array('status'=>429));}
    $lock='mit_request_'.substr($request_hash,0,32);
    $previous_lock=get_option($lock);if($previous_lock && (int)$previous_lock<time()-120){delete_option($lock);}
    if(!add_option($lock,time(),'',false)){return new WP_Error('mit_pending','This enquiry is being saved. Please wait a moment, then try again.',array('status'=>409));}
    $reference='MIT-'.gmdate('ymd').'-'.strtoupper(wp_generate_password(6,false,false));
    $record=array('reference'=>$reference,'name'=>$name,'email'=>$email,'phone'=>$phone,'interest'=>$interest,'timeline'=>$timeline,'budget'=>$budget===''?'':round((float)$budget),'message'=>$message,'source'=>mit_text_slice(sanitize_text_field($data['source']??'/contact/'),200),'submitted_at'=>gmdate('c'),'contact_consent'=>true,'marketing_consent'=>($data['marketing']??false)===true,'consent_version'=>'2026-10-08');
    $id=wp_insert_post(array('post_type'=>'mit_enquiry','post_status'=>'private','post_title'=>$reference.' · '.$name,'meta_input'=>array('_mit_enquiry'=>$record,'_mit_request_hash'=>$request_hash,'_mit_lead_status'=>'new','_mit_legal_hold'=>'0')),true);
    delete_option($lock);
    if(is_wp_error($id)||!$id){return new WP_Error('mit_storage','Your enquiry could not be saved. Please try again.',array('status'=>500));}
    set_transient($limit_key,$count+1,HOUR_IN_SECONDS);
    $settings=get_option('mit_site_settings',array());
    if($settings['notifications']??true){
        $inbox=$settings['notification_email']??'';if(!$inbox){$inbox=get_option('admin_email');}
        $body="A new move enquiry is saved in WordPress.\n\nReference: ".$reference."\nInterest: ".$interest."\nTimeline: ".$timeline."\n\nReview the enquiry in your private administration area:\n".admin_url('post.php?post='.$id.'&action=edit');
        $sent=is_email($inbox)?wp_mail($inbox,'Move In Thailand enquiry '.$reference,$body):false;
        update_post_meta($id,'_mit_notification',$sent?'accepted':'failed');
    }else{update_post_meta($id,'_mit_notification','disabled');}
    $response=new WP_REST_Response(array('saved'=>true,'reference'=>$reference),201);$response->header('Cache-Control','no-store, private');return $response;
}

/* Recoverable retention: no permanent deletion in this plugin. */
add_action('init',function(){if(!wp_next_scheduled('mit_retention_daily')){wp_schedule_event(time()+HOUR_IN_SECONDS,'daily','mit_retention_daily');}},40);
add_action('mit_retention_daily',function(){
    $ids=get_posts(array('post_type'=>'mit_enquiry','post_status'=>'private','numberposts'=>100,'fields'=>'ids','date_query'=>array(array('before'=>gmdate('Y-m-d H:i:s',time()-180*DAY_IN_SECONDS),'inclusive'=>true)),'suppress_filters'=>true));
    foreach($ids as $id){if(get_post_meta($id,'_mit_lead_status',true)==='active'||get_post_meta($id,'_mit_legal_hold',true)==='1'){continue;}wp_trash_post($id);}
});
