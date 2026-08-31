<?php
/**
 * Plugin Name: Casa Listings
 * Description: Registers the property listing content type, its taxonomies and
 *              meta fields. Installed as a must-use plugin so it cannot be
 *              deactivated by accident and taxonomies never vanish under a
 *              theme switch.
 * Version:     0.1.0
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

const CASA_LISTING_POST_TYPE = 'listing';
const CASA_LISTING_REF_META  = '_casa_reference';

/**
 * Meta fields we store per listing, and the type each is registered with.
 * Keys are the meta_key without the leading underscore convention so they are
 * readable in the editor and exposed to REST for headless/front-end use.
 */
function casa_listing_meta_schema(): array {
	return array(
		'casa_reference'     => 'string',
		'casa_price'         => 'number',
		'casa_rent_price'    => 'number',
		'casa_currency'      => 'string',
		'casa_deal_type'     => 'string',
		'casa_bedrooms'      => 'integer',
		'casa_bathrooms'     => 'number',
		'casa_size_sqm'      => 'number',
		'casa_land_sqm'      => 'number',
		'casa_floor'         => 'string',
		'casa_address'       => 'string',
		'casa_latitude'      => 'number',
		'casa_longitude'     => 'number',
		'casa_project'       => 'string',
		'casa_status'        => 'string',
		'casa_source_url'    => 'string',
		'casa_image_urls'    => 'string',
	);
}

add_action( 'init', 'casa_register_listing_post_type' );
function casa_register_listing_post_type(): void {
	register_post_type(
		CASA_LISTING_POST_TYPE,
		array(
			'labels'       => array(
				'name'               => __( 'Listings', 'casa' ),
				'singular_name'      => __( 'Listing', 'casa' ),
				'add_new_item'       => __( 'Add New Listing', 'casa' ),
				'edit_item'          => __( 'Edit Listing', 'casa' ),
				'search_items'       => __( 'Search Listings', 'casa' ),
				'not_found'          => __( 'No listings found', 'casa' ),
			),
			'public'       => true,
			'has_archive'  => 'properties',
			'menu_icon'    => 'dashicons-admin-home',
			'menu_position'=> 20,
			'rewrite'      => array( 'slug' => 'property', 'with_front' => false ),
			'supports'     => array( 'title', 'editor', 'thumbnail', 'excerpt', 'revisions' ),
			'show_in_rest' => true,
			'taxonomies'   => array( 'listing_location', 'listing_type', 'listing_feature' ),
		)
	);

	casa_register_listing_taxonomy( 'listing_location', __( 'Locations', 'casa' ), __( 'Location', 'casa' ), 'location', true );
	casa_register_listing_taxonomy( 'listing_type', __( 'Property Types', 'casa' ), __( 'Property Type', 'casa' ), 'property-type', true );
	casa_register_listing_taxonomy( 'listing_feature', __( 'Features', 'casa' ), __( 'Feature', 'casa' ), 'feature', false );

	foreach ( casa_listing_meta_schema() as $key => $type ) {
		register_post_meta(
			CASA_LISTING_POST_TYPE,
			$key,
			array(
				'type'          => $type,
				'single'        => true,
				'show_in_rest'  => true,
				'auth_callback' => static function (): bool {
					return current_user_can( 'edit_posts' );
				},
			)
		);
	}
}

function casa_register_listing_taxonomy(
	string $slug,
	string $plural,
	string $singular,
	string $rewrite,
	bool $hierarchical
): void {
	register_taxonomy(
		$slug,
		array( CASA_LISTING_POST_TYPE ),
		array(
			'labels'            => array( 'name' => $plural, 'singular_name' => $singular ),
			'hierarchical'      => $hierarchical,
			'public'            => true,
			'show_admin_column' => true,
			'show_in_rest'      => true,
			'rewrite'           => array( 'slug' => $rewrite, 'with_front' => false ),
		)
	);
}

/**
 * Find an existing listing by its agency reference, so re-importing an export
 * updates rows instead of duplicating them.
 */
function casa_find_listing_by_reference( string $reference ): ?int {
	if ( '' === $reference ) {
		return null;
	}

	$found = get_posts(
		array(
			'post_type'        => CASA_LISTING_POST_TYPE,
			'post_status'      => 'any',
			'numberposts'      => 1,
			'fields'           => 'ids',
			'meta_key'         => CASA_LISTING_REF_META,
			'meta_value'       => $reference,
			'suppress_filters' => false,
		)
	);

	return $found ? (int) $found[0] : null;
}

/**
 * Show the reference and price in the admin list -- the two columns anyone
 * managing inventory actually scans for.
 */
add_filter( 'manage_' . CASA_LISTING_POST_TYPE . '_posts_columns', 'casa_listing_columns' );
function casa_listing_columns( array $columns ): array {
	$insert = array(
		'casa_reference' => __( 'Ref', 'casa' ),
		'casa_price'     => __( 'Price', 'casa' ),
	);
	$offset = array_search( 'date', array_keys( $columns ), true );
	if ( false === $offset ) {
		return $columns + $insert;
	}
	return array_slice( $columns, 0, $offset, true )
		+ $insert
		+ array_slice( $columns, $offset, null, true );
}

add_action( 'manage_' . CASA_LISTING_POST_TYPE . '_posts_custom_column', 'casa_listing_column_value', 10, 2 );
function casa_listing_column_value( string $column, int $post_id ): void {
	if ( ! in_array( $column, array( 'casa_reference', 'casa_price' ), true ) ) {
		return;
	}

	$value = get_post_meta( $post_id, $column, true );

	if ( 'casa_price' === $column ) {
		$rent = get_post_meta( $post_id, 'casa_rent_price', true );
		$parts = array();
		if ( $value ) {
			$parts[] = number_format( (float) $value );
		}
		if ( $rent ) {
			/* translators: %s: formatted monthly rent */
			$parts[] = sprintf( __( '%s /mo', 'casa' ), number_format( (float) $rent ) );
		}
		$value = $parts ? implode( ' &middot; ', $parts ) : '&mdash;';
		echo wp_kses( $value, array() );
		return;
	}

	echo esc_html( $value ? (string) $value : '—' );
}
