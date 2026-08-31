<?php
/**
 * Plugin Name: Casa Listings — Display
 * Description: Templates, helpers and styles for the listing post type. Kept
 *              separate from registration so the data model can exist without
 *              the presentation, and so a theme can override either one.
 * Version:     0.1.0
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'CASA_TEMPLATE_DIR', __DIR__ . '/casa-templates' );

/**
 * Load one of our templates. A theme wins if it ships its own copy, so a
 * designer can override any of this without touching the plugin.
 */
function casa_template( string $file ): void {
	$theme = locate_template( array( "casa/{$file}" ) );
	if ( $theme ) {
		load_template( $theme, false );
		return;
	}
	$path = CASA_TEMPLATE_DIR . '/' . $file;
	if ( file_exists( $path ) ) {
		load_template( $path, false );
	}
}

/**
 * Route listing archives and single listings to our templates, unless the
 * active theme already provides one.
 */
add_filter( 'template_include', 'casa_template_include' );
function casa_template_include( string $template ): string {
	$is_single  = is_singular( 'listing' );
	$is_archive = is_post_type_archive( 'listing' )
		|| is_tax( array( 'listing_location', 'listing_type', 'listing_feature' ) );

	if ( ! $is_single && ! $is_archive ) {
		return $template;
	}

	// A theme template for this post type takes precedence over ours.
	$theme_template = $is_single
		? locate_template( array( 'single-listing.php' ) )
		: locate_template( array( 'archive-listing.php' ) );
	if ( $theme_template ) {
		return $theme_template;
	}

	$ours = CASA_TEMPLATE_DIR . '/' . ( $is_single ? 'single-listing.php' : 'archive-listing.php' );
	return file_exists( $ours ) ? $ours : $template;
}

add_action( 'wp_enqueue_scripts', 'casa_enqueue_styles' );
function casa_enqueue_styles(): void {
	if ( ! is_singular( 'listing' )
		&& ! is_post_type_archive( 'listing' )
		&& ! is_tax( array( 'listing_location', 'listing_type', 'listing_feature' ) ) ) {
		return;
	}
	wp_register_style( 'casa-listings', false, array(), '0.1.0' );
	wp_enqueue_style( 'casa-listings' );
	wp_add_inline_style( 'casa-listings', casa_inline_css() );
}

/**
 * Prices come from agency exports in mixed currencies, and a listing can be
 * for sale, for rent, or both.
 */
function casa_format_price( $price, $rent, string $currency = 'THB' ): string {
	$symbol = 'THB' === $currency ? '฿' : ( 'USD' === $currency ? '$' : $currency . ' ' );
	$parts  = array();

	if ( $price ) {
		$parts[] = $symbol . number_format( (float) $price );
	}
	if ( $rent ) {
		/* translators: %s: formatted monthly rent */
		$parts[] = sprintf( __( '%s / month', 'casa' ), $symbol . number_format( (float) $rent ) );
	}
	if ( ! $parts ) {
		return __( 'Price on application', 'casa' );
	}
	return implode( '  ·  ', $parts );
}

function casa_with_unit( $value, string $unit ): string {
	if ( ! $value ) {
		return '';
	}
	return rtrim( rtrim( (string) $value, '0' ), '.' ) . ' ' . $unit;
}

/**
 * Breadcrumbs double as the archive links search engines follow.
 */
function casa_breadcrumbs( $term = null ): string {
	$archive = get_post_type_archive_link( 'listing' );
	$crumbs  = array(
		'<a href="' . esc_url( home_url( '/' ) ) . '">' . esc_html__( 'Home', 'casa' ) . '</a>',
		'<a href="' . esc_url( $archive ) . '">' . esc_html__( 'Properties', 'casa' ) . '</a>',
	);
	if ( $term && ! is_wp_error( $term ) && isset( $term->name ) ) {
		$crumbs[] = '<a href="' . esc_url( get_term_link( $term ) ) . '">' . esc_html( $term->name ) . '</a>';
	}
	return '<nav class="casa-crumbs" aria-label="' . esc_attr__( 'Breadcrumb', 'casa' ) . '">'
		. implode( '<span aria-hidden="true"> / </span>', $crumbs )
		. '</nav>';
}

/**
 * A GET-based filter bar. No JavaScript: it degrades to plain links and the
 * results stay linkable and indexable.
 */
function casa_filter_bar(): string {
	$locations = get_terms( array( 'taxonomy' => 'listing_location', 'hide_empty' => true ) );
	$types     = get_terms( array( 'taxonomy' => 'listing_type', 'hide_empty' => true ) );
	if ( ( ! $locations || is_wp_error( $locations ) ) && ( ! $types || is_wp_error( $types ) ) ) {
		return '';
	}

	$out  = '<form class="casa-filters" method="get" action="' . esc_url( get_post_type_archive_link( 'listing' ) ) . '">';
	$out .= casa_filter_select( 'listing_location', __( 'Any area', 'casa' ), $locations );
	$out .= casa_filter_select( 'listing_type', __( 'Any type', 'casa' ), $types );
	$out .= '<label class="casa-filters__field"><span>' . esc_html__( 'Bedrooms', 'casa' ) . '</span>';
	$out .= '<select name="beds"><option value="">' . esc_html__( 'Any', 'casa' ) . '</option>';
	foreach ( array( 1, 2, 3, 4, 5 ) as $n ) {
		$sel  = selected( (string) $n, (string) filter_input( INPUT_GET, 'beds' ), false );
		$out .= '<option value="' . esc_attr( (string) $n ) . '"' . $sel . '>' . esc_html( $n . '+' ) . '</option>';
	}
	$out .= '</select></label>';
	$out .= '<button type="submit">' . esc_html__( 'Search', 'casa' ) . '</button>';
	$out .= '</form>';
	return $out;
}

function casa_filter_select( string $taxonomy, string $any_label, $terms ): string {
	if ( ! $terms || is_wp_error( $terms ) ) {
		return '';
	}
	$current = (string) filter_input( INPUT_GET, $taxonomy );
	$label   = 'listing_location' === $taxonomy ? __( 'Area', 'casa' ) : __( 'Type', 'casa' );

	$out = '<label class="casa-filters__field"><span>' . esc_html( $label ) . '</span>';
	$out .= '<select name="' . esc_attr( $taxonomy ) . '">';
	$out .= '<option value="">' . esc_html( $any_label ) . '</option>';
	foreach ( $terms as $term ) {
		$out .= '<option value="' . esc_attr( $term->slug ) . '"' . selected( $term->slug, $current, false ) . '>'
			. esc_html( $term->name ) . '</option>';
	}
	return $out . '</select></label>';
}

/**
 * Filter the archive by the bedroom count, which is meta rather than a term.
 */
add_action( 'pre_get_posts', 'casa_apply_bed_filter' );
function casa_apply_bed_filter( WP_Query $query ): void {
	if ( is_admin() || ! $query->is_main_query() ) {
		return;
	}
	if ( ! $query->is_post_type_archive( 'listing' )
		&& ! $query->is_tax( array( 'listing_location', 'listing_type', 'listing_feature' ) ) ) {
		return;
	}
	$beds = (int) filter_input( INPUT_GET, 'beds' );
	if ( $beds > 0 ) {
		$query->set(
			'meta_query',
			array(
				array(
					'key'     => 'casa_bedrooms',
					'value'   => $beds,
					'type'    => 'NUMERIC',
					'compare' => '>=',
				),
			)
		);
	}
}

/**
 * Related properties: same area first, then same type. These are the links
 * that keep a visitor on the site instead of back on Google.
 */
function casa_related( int $post_id, int $limit = 3 ): string {
	$locations = wp_get_object_terms( $post_id, 'listing_location', array( 'fields' => 'ids' ) );
	$types     = wp_get_object_terms( $post_id, 'listing_type', array( 'fields' => 'ids' ) );

	$tax_query = array( 'relation' => 'OR' );
	if ( $locations && ! is_wp_error( $locations ) ) {
		$tax_query[] = array( 'taxonomy' => 'listing_location', 'field' => 'term_id', 'terms' => $locations );
	}
	if ( $types && ! is_wp_error( $types ) ) {
		$tax_query[] = array( 'taxonomy' => 'listing_type', 'field' => 'term_id', 'terms' => $types );
	}
	if ( count( $tax_query ) < 2 ) {
		return '';
	}

	$related = new WP_Query(
		array(
			'post_type'           => 'listing',
			'posts_per_page'      => $limit,
			'post__not_in'        => array( $post_id ),
			'ignore_sticky_posts' => true,
			'tax_query'           => $tax_query,
		)
	);
	if ( ! $related->have_posts() ) {
		return '';
	}

	ob_start();
	echo '<section class="casa-related"><h2 class="casa-h2">' . esc_html__( 'You might also like', 'casa' ) . '</h2>';
	echo '<div class="casa-grid">';
	while ( $related->have_posts() ) {
		$related->the_post();
		casa_template( 'parts-card.php' );
	}
	echo '</div></section>';
	wp_reset_postdata();
	return (string) ob_get_clean();
}

/**
 * Browse-by links. Cheap internal linking that gives every area and property
 * type an indexable route in from any listing page.
 */
function casa_browse_links(): string {
	$sections = array(
		__( 'Browse by area', 'casa' ) => 'listing_location',
		__( 'Browse by type', 'casa' ) => 'listing_type',
	);

	$out = '';
	foreach ( $sections as $heading => $taxonomy ) {
		$terms = get_terms( array( 'taxonomy' => $taxonomy, 'hide_empty' => true, 'number' => 24 ) );
		if ( ! $terms || is_wp_error( $terms ) ) {
			continue;
		}
		$out .= '<h2 class="casa-h2">' . esc_html( $heading ) . '</h2><ul class="casa-chips">';
		foreach ( $terms as $term ) {
			$out .= '<li><a href="' . esc_url( get_term_link( $term ) ) . '">'
				. esc_html( $term->name )
				. ' <span>' . esc_html( (string) $term->count ) . '</span></a></li>';
		}
		$out .= '</ul>';
	}
	return $out ? '<section class="casa-browse">' . $out . '</section>' : '';
}

/**
 * Styles ship inline and scoped to `.casa`, so they cannot leak into the rest
 * of the theme and need no build step or extra request.
 */
function casa_inline_css(): string {
	return '
.casa{--casa-gap:1.5rem;--casa-radius:10px;--casa-line:rgba(0,0,0,.12);--casa-muted:#5c6b68;max-width:76rem;margin:0 auto;padding:2rem 1.25rem 4rem}
.casa *,.casa *::before,.casa *::after{box-sizing:border-box}
.casa-crumbs{font-size:.85rem;color:var(--casa-muted);margin-bottom:.5rem}
.casa-crumbs a{color:inherit}
.casa-head__title{font-size:clamp(1.8rem,4vw,2.6rem);line-height:1.1;margin:.2rem 0;text-wrap:balance}
.casa-head__price{font-size:1.4rem;font-weight:600;margin:.35rem 0}
.casa-head__count{color:var(--casa-muted);margin:.25rem 0 0}
.casa-filters{display:flex;flex-wrap:wrap;gap:.75rem;align-items:end;margin:1.5rem 0;padding:1rem;border:1px solid var(--casa-line);border-radius:var(--casa-radius)}
.casa-filters__field{display:flex;flex-direction:column;gap:.25rem;font-size:.8rem;color:var(--casa-muted)}
.casa-filters select{padding:.45rem .6rem;border:1px solid var(--casa-line);border-radius:6px;font:inherit;min-width:10rem}
.casa-filters button{padding:.55rem 1.25rem;border:0;border-radius:6px;background:#14524c;color:#fff;font:inherit;font-weight:600;cursor:pointer}
.casa-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(17rem,1fr));gap:var(--casa-gap);margin:1.5rem 0}
.casa-card{border:1px solid var(--casa-line);border-radius:var(--casa-radius);overflow:hidden;display:flex;flex-direction:column}
.casa-card__media{position:relative;display:block;aspect-ratio:4/3;overflow:hidden;background:#e8eceb}
.casa-card__media img{width:100%;height:100%;object-fit:cover;display:block}
.casa-card__placeholder{position:absolute;inset:0;background:linear-gradient(135deg,#dfe6e4,#c8d4d1)}
.casa-card__tag{position:absolute;top:.6rem;left:.6rem;background:#14524c;color:#fff;font-size:.7rem;font-weight:600;letter-spacing:.04em;text-transform:uppercase;padding:.2rem .5rem;border-radius:100px}
.casa-card__tag--rent{background:#8a5a08}
.casa-card__body{padding:.9rem 1rem 1.1rem;display:flex;flex-direction:column;gap:.35rem;flex:1}
.casa-card__place{font-size:.78rem;text-transform:uppercase;letter-spacing:.06em;color:var(--casa-muted);text-decoration:none}
.casa-card__title{font-size:1.05rem;line-height:1.3;margin:0}
.casa-card__title a{text-decoration:none;color:inherit}
.casa-card__price{font-weight:600;margin:.1rem 0}
.casa-card__facts{list-style:none;display:flex;flex-wrap:wrap;gap:.9rem;padding:0;margin:.25rem 0 0;font-size:.85rem;color:var(--casa-muted)}
.casa-card__ref{margin:.5rem 0 0;font-size:.72rem;color:var(--casa-muted);font-family:ui-monospace,monospace}
.casa-single__grid{display:grid;grid-template-columns:minmax(0,2fr) minmax(15rem,1fr);gap:2rem;margin-top:1.5rem}
@media (max-width:52rem){.casa-single__grid{grid-template-columns:1fr}}
.casa-gallery__main img{width:100%;height:auto;border-radius:var(--casa-radius)}
.casa-gallery__thumbs{display:grid;grid-template-columns:repeat(auto-fill,minmax(6rem,1fr));gap:.5rem;margin-top:.5rem}
.casa-gallery__thumbs img{width:100%;aspect-ratio:1;object-fit:cover;border-radius:6px}
.casa-specs{width:100%;border-collapse:collapse;font-size:.92rem}
.casa-specs th,.casa-specs td{text-align:left;padding:.5rem .25rem;border-bottom:1px solid var(--casa-line)}
.casa-specs th{color:var(--casa-muted);font-weight:500}
.casa-h2{font-size:1.25rem;margin:2rem 0 .75rem}
.casa-features,.casa-chips{list-style:none;display:flex;flex-wrap:wrap;gap:.5rem;padding:0;margin:0}
.casa-features a,.casa-chips a{display:inline-block;padding:.3rem .7rem;border:1px solid var(--casa-line);border-radius:100px;font-size:.85rem;text-decoration:none;color:inherit}
.casa-chips span{color:var(--casa-muted);font-size:.8rem}
.casa-pagination{display:flex;gap:.4rem;justify-content:center;margin:2rem 0}
.casa-pagination .page-numbers{padding:.35rem .7rem;border:1px solid var(--casa-line);border-radius:6px;text-decoration:none;color:inherit}
.casa-pagination .current{background:#14524c;color:#fff;border-color:#14524c}
.casa-empty{padding:2rem;text-align:center;color:var(--casa-muted)}
@media (prefers-color-scheme:dark){.casa{--casa-line:rgba(255,255,255,.16);--casa-muted:#9aa8a5}.casa-card__media{background:#222c2a}.casa-card__placeholder{background:linear-gradient(135deg,#2a3634,#141d1b)}}
';
}
