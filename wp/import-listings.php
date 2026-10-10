<?php
/**
 * Listing importer, executed by WP-CLI:
 *
 *   wp eval-file import-listings.php /path/to/listings.json [--sideload-images]
 *
 * Reads the JSON produced by `bin/provision` / `bin/import-listings` and
 * upserts one post per listing, keyed on the agency reference so re-running an
 * export updates rows rather than duplicating them.
 *
 * Written to be re-runnable: nothing here destroys a listing an editor has
 * since improved by hand except the fields the CSV is authoritative for.
 */

if ( ! defined( 'WP_CLI' ) || ! WP_CLI ) {
	return;
}

$path = $args[0] ?? '';
if ( '' === $path || ! file_exists( $path ) ) {
	WP_CLI::error( "listing payload not found: {$path}" );
}

$sideload_images = in_array( '--sideload-images', $args, true );

$payload = json_decode( (string) file_get_contents( $path ), true );
if ( ! is_array( $payload ) ) {
	WP_CLI::error( "could not parse JSON at {$path}" );
}

$rows = $payload['listings'] ?? array();
if ( ! is_array( $rows ) || ! $rows ) {
	WP_CLI::warning( 'payload contained no listings; nothing to do' );
	return;
}

if ( ! post_type_exists( 'listing' ) ) {
	WP_CLI::error(
		'the "listing" post type is not registered. Install the Casa Listings '
		. 'mu-plugin first (bin/provision does this automatically).'
	);
}

$created = 0;
$updated = 0;
$skipped = 0;
$images  = 0;

$progress = \WP_CLI\Utils\make_progress_bar( 'Importing listings', count( $rows ) );

foreach ( $rows as $row ) {
	$reference = trim( (string) ( $row['reference'] ?? '' ) );
	$title     = trim( (string) ( $row['title'] ?? '' ) );

	if ( '' === $title ) {
		++$skipped;
		$progress->tick();
		continue;
	}

	$existing = $reference ? casa_find_listing_by_reference( $reference ) : null;

	$postarr = array(
		'post_type'    => 'listing',
		'post_title'   => $title,
		'post_content' => (string) ( $row['description'] ?? '' ),
		'post_status'  => 'publish',
	);

	if ( $existing ) {
		$postarr['ID'] = $existing;
		$post_id       = wp_update_post( $postarr, true );
	} else {
		$post_id = wp_insert_post( $postarr, true );
	}

	if ( is_wp_error( $post_id ) ) {
		WP_CLI::warning( "{$title}: " . $post_id->get_error_message() );
		++$skipped;
		$progress->tick();
		continue;
	}

	$existing ? $updated++ : $created++;

	// The reference is stored twice on purpose: the private key we look up by,
	// and a public-facing copy exposed through REST.
	if ( $reference ) {
		update_post_meta( $post_id, '_casa_reference', $reference );
	}

	$meta_map = array(
		'casa_reference'  => $reference,
		'casa_price'      => $row['price'] ?? null,
		'casa_rent_price' => $row['rent_price'] ?? null,
		'casa_currency'   => $row['currency'] ?? 'THB',
		'casa_deal_type'  => $row['deal_type'] ?? '',
		'casa_bedrooms'   => $row['bedrooms'] ?? null,
		'casa_bathrooms'  => $row['bathrooms'] ?? null,
		'casa_size_sqm'   => $row['size_sqm'] ?? null,
		'casa_land_sqm'   => $row['land_sqm'] ?? null,
		'casa_floor'      => $row['floor'] ?? '',
		'casa_address'    => $row['address'] ?? '',
		'casa_latitude'   => $row['latitude'] ?? null,
		'casa_longitude'  => $row['longitude'] ?? null,
		'casa_project'    => $row['project'] ?? '',
		'casa_status'     => $row['status'] ?? '',
		'casa_source_url' => $row['url'] ?? '',
	);

	foreach ( $meta_map as $key => $value ) {
		if ( null === $value || '' === $value ) {
			delete_post_meta( $post_id, $key );
			continue;
		}
		update_post_meta( $post_id, $key, $value );
	}

	$image_urls = array_filter( (array) ( $row['images'] ?? array() ) );
	if ( $image_urls ) {
		update_post_meta( $post_id, 'casa_image_urls', implode( "\n", $image_urls ) );
	}

	// Taxonomies. Terms are created on demand; append=false so removing a
	// value from the CSV removes it from the site too.
	if ( ! empty( $row['location'] ) ) {
		wp_set_object_terms( $post_id, (string) $row['location'], 'listing_location', false );
	}
	if ( ! empty( $row['property_type'] ) ) {
		wp_set_object_terms( $post_id, (string) $row['property_type'], 'listing_type', false );
	}
	if ( ! empty( $row['features'] ) && is_array( $row['features'] ) ) {
		wp_set_object_terms( $post_id, array_map( 'strval', $row['features'] ), 'listing_feature', false );
	}

	// Featured image. Off by default: sideloading hundreds of remote images is
	// slow and will trip shared-host limits, so it is opt-in per run.
	if ( $sideload_images && $image_urls && ! has_post_thumbnail( $post_id ) ) {
		require_once ABSPATH . 'wp-admin/includes/media.php';
		require_once ABSPATH . 'wp-admin/includes/file.php';
		require_once ABSPATH . 'wp-admin/includes/image.php';

		$attachment_id = media_sideload_image( (string) $image_urls[0], $post_id, $title, 'id' );
		if ( is_wp_error( $attachment_id ) ) {
			WP_CLI::debug( "{$title}: image failed -- " . $attachment_id->get_error_message() );
		} else {
			set_post_thumbnail( $post_id, $attachment_id );
			++$images;
		}
	}

	$progress->tick();
}

$progress->finish();

WP_CLI::success(
	sprintf(
		'%d created, %d updated, %d skipped, %d featured images.',
		$created,
		$updated,
		$skipped,
		$images
	)
);
