from visualization import dashboard


def test_dashboard_exports_analysis_renderer():
    assert callable(dashboard.render_analysis)
