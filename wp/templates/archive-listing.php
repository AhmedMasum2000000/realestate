<?php
/**
 * Listings archive: filter bar, results grid, pagination.
 *
 * Used for the `listing` post archive and for its taxonomy archives
 * (location, property type, feature).
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

get_header();

$term        = is_tax() ? get_queried_object() : null;
$heading     = $term ? $term->name : __( 'Properties', 'casa' );
$description = $term ? term_description( $term ) : '';
?>
<main id="casa-main" class="casa">

	<header class="casa-head">
		<?php echo wp_kses_post( casa_breadcrumbs( $term ) ); ?>
		<h1 class="casa-head__title"><?php echo esc_html( $heading ); ?></h1>
		<?php if ( $description ) : ?>
			<div class="casa-head__intro"><?php echo wp_kses_post( $description ); ?></div>
		<?php endif; ?>
		<p class="casa-head__count">
			<?php
			$total = (int) $GLOBALS['wp_query']->found_posts;
			printf(
				/* translators: %s: number of properties found */
				esc_html( _n( '%s property', '%s properties', $total, 'casa' ) ),
				esc_html( number_format_i18n( $total ) )
			);
			?>
		</p>
	</header>

	<?php echo wp_kses_post( casa_filter_bar() ); ?>

	<?php if ( have_posts() ) : ?>
		<div class="casa-grid">
			<?php
			while ( have_posts() ) :
				the_post();
				casa_template( 'parts-card.php' );
			endwhile;
			?>
		</div>

		<nav class="casa-pagination" aria-label="<?php esc_attr_e( 'Properties', 'casa' ); ?>">
			<?php
			echo wp_kses_post(
				paginate_links(
					array(
						'prev_text' => __( 'Previous', 'casa' ),
						'next_text' => __( 'Next', 'casa' ),
					)
				)
			);
			?>
		</nav>
	<?php else : ?>
		<p class="casa-empty">
			<?php esc_html_e( 'No properties match this search yet.', 'casa' ); ?>
			<a href="<?php echo esc_url( get_post_type_archive_link( 'listing' ) ); ?>">
				<?php esc_html_e( 'See all properties', 'casa' ); ?>
			</a>
		</p>
	<?php endif; ?>

	<?php echo wp_kses_post( casa_browse_links() ); ?>

</main>
<?php
get_footer();
