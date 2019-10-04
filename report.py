#!/usr/bin/env python

""" report.py: Functions to generate graphs displaying qc information about data """

__author__ = "Bryan Roberts"

import plotly.graph_objects as go


def chart_feature_cv(df):
    """ charts cv of features in samples and pools
    Parameters:
            df (data-frame): data frame from process.py

    Returns:
            None

    """

    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=(
                        'Metabolite name', 'Sample %CV', 'Pool %CV'), fill_color='paleturquoise', line_color='black', font=dict(
                        color='black', size=14), align='left'), cells=dict(
                            values=[
                                df['Metabolite name'], df['Sample %CV'], df['Pool %CV']], align='left', font=dict(
                                    color='black', size=12), line_color='black', fill_color=(
                                        'white', [
                                            'red' if val >= 20 else 'green' for val in df['Sample %CV']], [
                                                'red' if val >= 20 else 'green' for val in df['Pool %CV']])))])

    fig.show()


def number_of_features_changed(
        known_before,
        known_after,
        unknown_before,
        unknown_after):
    """ charts number of features for knowns and unknowns before and after reduction
    Parameters:
            known_before (int): number of known features before reduction
            known_after (int): number of known features after reduction
            unknown_before (int): number of unknown features before reduction
            unknown_before (int): number of unknown features after reduction

    Returns:
            None

    """

    feature_type = ['Known', 'Unknown', 'Total']
    before_reduction = [known_before, unknown_before, known_before + unknown_before]
    after_reduction = [known_after, unknown_after, known_after + unknown_after]

    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=(
                        'Feature Type',
                        'Features Before Reduction',
                        'Features After Reduction'),
                    fill_color='paleturquoise',
                    line_color='black',
                    font=dict(
                        color='black',
                        size=14),
                    align='left'),
                cells=dict(
                    values=[
                        feature_type,
                        before_reduction,
                        after_reduction],
                    align='left',
                    font=dict(
                        color='black',
                        size=12),
                    line_color='black',
                    fill_color='white'))])

    fig.show()
