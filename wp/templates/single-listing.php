<?php
/**
 * One property: gallery, specification table, description, and the cross-links
 * that keep a visitor moving -- same area, same type, similar price.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

get_header();

while ( have_posts() ) :
	the_post();

	$id       = get_the_ID();
	$ref      = get_post_meta( $id, 'casa_reference', true );
	$price    = get_post_meta( $id, 'casa_price', true );
	$rent     = get_post_meta( $id, 'casa_rent_price', true );
	$currency = get_post_meta( $id, 'casa_currency', true ) ?: 'THB';
	$images   = array_filter( explode( "\n", (string) get_post_meta( $id, 'casa_image_urls', true ) ) );

	$specs = array(
		__( 'Bedrooms', 'casa' )   => get_post_meta( $id, 'casa_bedrooms', true ),
		__( 'Bathrooms', 'casa' )  => get_post_meta( $id, 'casa_bathrooms', true ),
		__( 'Interior', 'casa' )   => casa_with_unit( get_post_meta( $id, 'casa_size_sqm', true ), 'sqm' ),
		__( 'Land', 'casa' )       => casa_with_unit( get_post_meta( $id, 'casa_land_sqm', true ), 'sqm' ),
		__( 'Floor', 'casa' )      => get_post_meta( $id, 'casa_floor', true ),
		__( 'Project', 'casa' )    => get_post_meta( $id, 'casa_project', true ),
		__( 'Reference', 'casa' )  => $ref,
	);

	$locations = get_the_terms( $id, 'listing_location' );
	$location  = ( $locations && ! is_wp_error( $locations ) ) ? $locations[0] : null;
	?>
	<main id="casa-main" class="casa casa--single">

		<header class="casa-head">
			<?php echo wp_kses_post( casa_breadcrumbs( $location ) ); ?>
			<h1 class="casa-head__title"><?php the_title(); ?></h1>
			<p class="casa-head__price"><?php echo esc_html( casa_format_price( $price, $rent, $currency ) ); ?></p>
		</header>

		<?php if ( has_post_thumbnail() || $images ) : ?>
			<div class="casa-gallery">
				<?php if ( has_post_thumbnail() ) : ?>
					<figure class="casa-gallery__main"><?php the_post_thumbnail( 'large' ); ?></figure>
				<?php endif; ?>
				<?php if ( count( $images ) > 1 ) : ?>
					<div class="casa-gallery__thumbs">
						<?php foreach ( array_slice( $images, 0, 8 ) as $url ) : ?>
							<img src="<?php echo esc_url( $url ); ?>" alt="" loading="lazy" />
						<?php endforeach; ?>
					</div>
				<?php endif; ?>
			</div>
		<?php endif; ?>

		<div class="casa-single__grid">
			<div class="casa-single__main">
				<div class="casa-prose"><?php the_content(); ?></div>

				<?php
				$features = get_the_terms( $id, 'listing_feature' );
				if ( $features && ! is_wp_error( $features ) ) :
					?>
					<h2 class="casa-h2"><?php esc_html_e( 'Features', 'casa' ); ?></h2>
					<ul class="casa-features">
						<?php foreach ( $features as $feature ) : ?>
							<li>
								<a href="<?php echo esc_url( get_term_link( $feature ) ); ?>">
									<?php echo esc_html( $feature->name ); ?>
								</a>
							</li>
						<?php endforeach; ?>
					</ul>
				<?php endif; ?>
			</div>

			<aside class="casa-single__aside">
				<table class="casa-specs">
					<caption class="screen-reader-text"><?php esc_html_e( 'Property details', 'casa' ); ?></caption>
					<tbody>
					<?php foreach ( $specs as $label => $value ) : ?>
						<?php if ( '' === $value || null === $value ) { continue; } ?>
						<tr>
							<th scope="row"><?php echo esc_html( $label ); ?></th>
							<td><?php echo esc_html( (string) $value ); ?></td>
						</tr>
					<?php endforeach; ?>
					</tbody>
				</table>
			</aside>
		</div>

		<?php echo wp_kses_post( casa_related( $id ) ); ?>
		<?php echo wp_kses_post( casa_browse_links() ); ?>

	</main>
	<?php
endwhile;

get_footer();
