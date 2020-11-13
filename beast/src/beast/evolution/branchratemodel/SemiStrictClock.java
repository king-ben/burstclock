package beast.evolution.branchratemodel;

import beast.core.Description;
import beast.core.Input;
import beast.core.parameter.RealParameter;
import beast.evolution.tree.Node;

@Description("A constant rate for each branch in the beast.tree, plus a constant contribution from each split in the tree")
public class SemiStrictClock extends StrictClockModel {
	public Input<RealParameter> persplit = new Input<RealParameter>("perSplit",
			"Effective number of changes after each split in the tree");
	public Input<RealParameter> birthrate = new Input<RealParameter>("birthrate",
			"Birth rate (not effective diversification rate) of the tree, used to infer additional changes after unobserved splits. (Not necessary, but likely makes for better mixing.)",
			new RealParameter(new Double[] { 0. }));

	@Override
	public double getRateForBranch(final Node node) {
		double blength = node.getLength();
		double mu = meanRateInput.get().getValue();
		return Math.max(
				((1 + blength * birthrate.get().getValue()) * persplit.get().getValue() + (blength * mu)) / blength,
				mu);
	}
}